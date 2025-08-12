#ifndef VECTOR_TYPES_H
#define VECTOR_TYPES_H

/*
 * CUDA vector_types.h compatibility header for non-CUDA builds
 * Provides basic vector type definitions when CUDA is not available
 */

#if defined(__cplusplus)
extern "C" {
#endif

// Basic vector types for compatibility
struct char1 {
    signed char x;
};

struct uchar1 {
    unsigned char x;
};

struct char2 {
    signed char x, y;
};

struct uchar2 {
    unsigned char x, y;
};

struct char3 {
    signed char x, y, z;
};

struct uchar3 {
    unsigned char x, y, z;
};

struct char4 {
    signed char x, y, z, w;
};

struct uchar4 {
    unsigned char x, y, z, w;
};

struct short1 {
    short x;
};

struct ushort1 {
    unsigned short x;
};

struct short2 {
    short x, y;
};

struct ushort2 {
    unsigned short x, y;
};

struct short3 {
    short x, y, z;
};

struct ushort3 {
    unsigned short x, y, z;
};

struct short4 {
    short x, y, z, w;
};

struct ushort4 {
    unsigned short x, y, z, w;
};

struct int1 {
    int x;
};

struct uint1 {
    unsigned int x;
};

struct int2 {
    int x, y;
};

struct uint2 {
    unsigned int x, y;
};

struct int3 {
    int x, y, z;
};

struct uint3 {
    unsigned int x, y, z;
};

struct int4 {
    int x, y, z, w;
};

struct uint4 {
    unsigned int x, y, z, w;
};

struct long1 {
    long int x;
};

struct ulong1 {
    unsigned long x;
};

struct long2 {
    long int x, y;
};

struct ulong2 {
    unsigned long int x, y;
};

struct long3 {
    long int x, y, z;
};

struct ulong3 {
    unsigned long int x, y, z;
};

struct long4 {
    long int x, y, z, w;
};

struct ulong4 {
    unsigned long int x, y, z, w;
};

struct longlong1 {
    long long int x;
};

struct ulonglong1 {
    unsigned long long int x;
};

struct longlong2 {
    long long int x, y;
};

struct ulonglong2 {
    unsigned long long int x, y;
};

struct longlong3 {
    long long int x, y, z;
};

struct ulonglong3 {
    unsigned long long int x, y, z;
};

struct longlong4 {
    long long int x, y, z, w;
};

struct ulonglong4 {
    unsigned long long int x, y, z, w;
};

struct float1 {
    float x;
};

struct float2 {
    float x, y;
};

struct float3 {
    float x, y, z;
};

struct float4 {
    float x, y, z, w;
};

struct double1 {
    double x;
};

struct double2 {
    double x, y;
};

struct double3 {
    double x, y, z;
};

struct double4 {
    double x, y, z, w;
};

// Type aliases for convenience
typedef struct char1 char1;
typedef struct uchar1 uchar1;
typedef struct char2 char2;
typedef struct uchar2 uchar2;
typedef struct char3 char3;
typedef struct uchar3 uchar3;
typedef struct char4 char4;
typedef struct uchar4 uchar4;
typedef struct short1 short1;
typedef struct ushort1 ushort1;
typedef struct short2 short2;
typedef struct ushort2 ushort2;
typedef struct short3 short3;
typedef struct ushort3 ushort3;
typedef struct short4 short4;
typedef struct ushort4 ushort4;
typedef struct int1 int1;
typedef struct uint1 uint1;
typedef struct int2 int2;
typedef struct uint2 uint2;
typedef struct int3 int3;
typedef struct uint3 uint3;
typedef struct int4 int4;
typedef struct uint4 uint4;
typedef struct long1 long1;
typedef struct ulong1 ulong1;
typedef struct long2 long2;
typedef struct ulong2 ulong2;
typedef struct long3 long3;
typedef struct ulong3 ulong3;
typedef struct long4 long4;
typedef struct ulong4 ulong4;
typedef struct longlong1 longlong1;
typedef struct ulonglong1 ulonglong1;
typedef struct longlong2 longlong2;
typedef struct ulonglong2 ulonglong2;
typedef struct longlong3 longlong3;
typedef struct ulonglong3 ulonglong3;
typedef struct longlong4 longlong4;
typedef struct ulonglong4 ulonglong4;
typedef struct float1 float1;
typedef struct float2 float2;
typedef struct float3 float3;
typedef struct float4 float4;
typedef struct double1 double1;
typedef struct double2 double2;
typedef struct double3 double3;
typedef struct double4 double4;

#if defined(__cplusplus)
}
#endif

#endif /* VECTOR_TYPES_H */
