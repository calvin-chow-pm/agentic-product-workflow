// Encode typeset evidence frames. No screen capture or browser interaction.
#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreVideo/CoreVideo.h>
#import <CoreGraphics/CoreGraphics.h>
#import <ImageIO/ImageIO.h>

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) { fprintf(stderr,"Supply video-manifest.json\n"); return 1; }
        NSError *error = nil;
        NSDictionary *manifest = [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argv[1]]] options:0 error:&error];
        NSURL *output = [NSURL fileURLWithPath:manifest[@"output"]];
        if ([[NSFileManager defaultManager] fileExistsAtPath:output.path]) [[NSFileManager defaultManager] removeItemAtURL:output error:&error];
        AVAssetWriter *writer = [[AVAssetWriter alloc] initWithURL:output fileType:AVFileTypeMPEG4 error:&error];
        NSDictionary *settings = @{AVVideoCodecKey:AVVideoCodecTypeH264, AVVideoWidthKey:@1600, AVVideoHeightKey:@900, AVVideoCompressionPropertiesKey:@{AVVideoAverageBitRateKey:@1500000,AVVideoMaxKeyFrameIntervalKey:@15}};
        AVAssetWriterInput *input = [AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo outputSettings:settings];
        input.expectsMediaDataInRealTime = NO;
        NSDictionary *attrs = @{(NSString *)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_32ARGB), (NSString *)kCVPixelBufferWidthKey:@1600, (NSString *)kCVPixelBufferHeightKey:@900, (NSString *)kCVPixelBufferCGImageCompatibilityKey:@YES, (NSString *)kCVPixelBufferCGBitmapContextCompatibilityKey:@YES};
        AVAssetWriterInputPixelBufferAdaptor *adaptor = [AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:input sourcePixelBufferAttributes:attrs];
        [writer addInput:input];
        if (![writer startWriting]) { fprintf(stderr,"Encoder failed: %s\n",writer.error.description.UTF8String); return 1; }
        [writer startSessionAtSourceTime:kCMTimeZero];
        int64_t second=0;
        for (NSDictionary *frame in manifest[@"frames"]) {
            CGImageSourceRef source=CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:frame[@"path"]],NULL);
            CGImageRef image=CGImageSourceCreateImageAtIndex(source,0,NULL);
            CVPixelBufferRef buffer=NULL;
            CVPixelBufferCreate(kCFAllocatorDefault,1600,900,kCVPixelFormatType_32ARGB,(__bridge CFDictionaryRef)attrs,&buffer);
            CVPixelBufferLockBaseAddress(buffer,0);
            CGColorSpaceRef space=CGColorSpaceCreateDeviceRGB();
            CGContextRef context=CGBitmapContextCreate(CVPixelBufferGetBaseAddress(buffer),1600,900,8,CVPixelBufferGetBytesPerRow(buffer),space,kCGImageAlphaNoneSkipFirst);
            CGContextDrawImage(context,CGRectMake(0,0,1600,900),image);
            CVPixelBufferUnlockBaseAddress(buffer,0);
            for (int i=0;i<[frame[@"duration"] intValue];i++) {
                while (!input.readyForMoreMediaData) [NSThread sleepForTimeInterval:0.01];
                if (![adaptor appendPixelBuffer:buffer withPresentationTime:CMTimeMake(second++,1)]) { fprintf(stderr,"Frame failed: %s\n",writer.error.description.UTF8String); return 1; }
            }
            CGContextRelease(context); CGColorSpaceRelease(space); CVPixelBufferRelease(buffer); CGImageRelease(image); CFRelease(source);
        }
        [writer endSessionAtSourceTime:CMTimeMake(second,1)];
        [input markAsFinished];
        dispatch_semaphore_t done=dispatch_semaphore_create(0);
        [writer finishWritingWithCompletionHandler:^{dispatch_semaphore_signal(done);}];
        dispatch_semaphore_wait(done,DISPATCH_TIME_FOREVER);
        if (writer.status != AVAssetWriterStatusCompleted) { fprintf(stderr,"Video failed: %s\n",writer.error.description.UTF8String); return 1; }
        AVURLAsset *asset=[AVURLAsset URLAssetWithURL:output options:nil];
        AVAssetImageGenerator *generator=[AVAssetImageGenerator assetImageGeneratorWithAsset:asset];
        generator.appliesPreferredTrackTransform=YES;
        CGImageRef decoded=[generator copyCGImageAtTime:kCMTimeZero actualTime:NULL error:&error];
        NSURL *preview=[[output URLByDeletingLastPathComponent] URLByAppendingPathComponent:@"video-first-frame.png"];
        CGImageDestinationRef destination=CGImageDestinationCreateWithURL((__bridge CFURLRef)preview,CFSTR("public.png"),1,NULL);
        if (decoded && destination) { CGImageDestinationAddImage(destination,decoded,NULL); CGImageDestinationFinalize(destination); }
        if (decoded) CGImageRelease(decoded); if(destination) CFRelease(destination);
        printf("Encoded %lld seconds: %s\n",second,output.path.UTF8String);
        printf("Decoded preview: %s\n",preview.path.UTF8String);
    }
    return 0;
}
