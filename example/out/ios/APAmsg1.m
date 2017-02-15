// generated from a.proto by py-protoc, NEVER CHANGE!!

#import "APAmsg1.h"
#import "BPBenum.h"
#import "APAmsg2.h"

/**
 * a1
a2
 */
@implementation APAmsg1
+ (NSDictionary *)modelContainerPropertyGenericClass {
  return @{
    @"amsg2_list" : NSClassFromString(@"APAmsg2"),
    @"benum_list" : NSClassFromString(@"BPBenum"),
    @"int_map" : @"NSNumber",
    @"amsg2_map" : @"APAmsg2"
  };
}
@end

