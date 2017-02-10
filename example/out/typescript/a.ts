// generated from a.proto by py-protoc, NEVER CHANGE!!

/// <reference path="./sub/b.ts" />

namespace ap {
  /**
   * a1
a2
   */
  export interface Amsg1 {
    /**
     *str前的注释
     */
    str : string;
    /**
     *int32后的注释
     */
    int_32 : number;
    /**
     *int64前的注释1
int64后的注释2
     */
    int_64 : number;
    float_ : number;
    double_ : number;
    bool_ : boolean;
    b_enum : bp.Benum;
    amsg2 : ap.Amsg2;
    amsg2_list : Array<ap.Amsg2>;
    str_list : Array<string>;
    benum_list : Array<number>;
  }

  export interface Amsg2 {
    id : string;
  }

}

