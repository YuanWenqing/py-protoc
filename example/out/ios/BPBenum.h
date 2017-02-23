// generated from sub/b.proto by py-protoc, NEVER CHANGE!!

#import <Foundation/Foundation.h>

typedef enum {
  /**
   * b0 before @zh(中文b0)
b0 after @en(english b0) @zh(中文b0 again)
   */
  B0 = 0,
  /**
   * b1 after @en(english b1) @zh(中文b1)
   */
  B1 = 1
} BPBenum;

BPBenum BPBenumValueOf(NSString *text);
NSString* BPBenumDescription(BPBenum value);

