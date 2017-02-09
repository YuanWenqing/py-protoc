// generated from sub/b.proto by py-protoc, NEVER CHANGE!!

#import "BPBenum.h"

BPBenum BPBenumValueOf(NSString *text) {
  if (text) {
    if ([text isEqualToString:@"B0"])
      return B0;
    else if ([text isEqualToString:@"B1"])
      return B1;
  }
  return -1;
}

NSString* BPBenumDescription(BPBenum value) {
  switch (value) {
    case B0:
      return @"B0";
    case B1:
      return @"B1";
  }
  return @"";
}

