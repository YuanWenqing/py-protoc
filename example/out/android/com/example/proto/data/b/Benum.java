// generated from sub/b.proto by py-protoc, NEVER CHANGE!!

package com.example.proto.data.b;

public enum Benum {
  /**
b0 before
b0 after
   */
  B0(0),
  /**
b1 after
   */
  B1(1);

  public static final Benum valueOf(int value) {
    switch (value) {
      case 0: return B0;
      case 1: return B1;
      default: return null;
    }
  }

  private final int value = -1;

  public int getValue() { return this.value; }

  private Benum(int value) { this.value = value; }

}

