code 1:
int add(int a,int b){
    int result=a+b;
    return result;
}
asm code:
"add":
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-20], edi
        mov     DWORD PTR [rbp-24], esi
        mov     edx, DWORD PTR [rbp-20]
        mov     eax, DWORD PTR [rbp-24]
        add     eax, edx
        mov     DWORD PTR [rbp-4], eax
        mov     eax, DWORD PTR [rbp-4]
        pop     rbp
        ret


code 2:
int subtract(int a,int b){
    int result;
    if(a>b)
        result=a-b;
    else
        result=b-a;
    return result;
}
asm code:
"subtract":
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-20], edi
        mov     DWORD PTR [rbp-24], esi
        mov     eax, DWORD PTR [rbp-20]
        cmp     eax, DWORD PTR [rbp-24]
        jle     .L2
        mov     eax, DWORD PTR [rbp-20]
        sub     eax, DWORD PTR [rbp-24]
        mov     DWORD PTR [rbp-4], eax
        jmp     .L3
.L2:
        mov     eax, DWORD PTR [rbp-24]
        sub     eax, DWORD PTR [rbp-20]
        mov     DWORD PTR [rbp-4], eax
.L3:
        mov     eax, DWORD PTR [rbp-4]
        pop     rbp
        ret


code 3:
int add_with_loop(int a){
    int result;
    for(int i=0;i<a;i++)
        result=result+i;
    return result;
}
asm code:
"add_with_loop":
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-20], edi
        mov     DWORD PTR [rbp-8], 0
        jmp     .L2
.L3:
        mov     eax, DWORD PTR [rbp-8]
        add     DWORD PTR [rbp-4], eax
        add     DWORD PTR [rbp-8], 1
.L2:
        mov     eax, DWORD PTR [rbp-8]
        cmp     eax, DWORD PTR [rbp-20]
        jl      .L3
        mov     eax, DWORD PTR [rbp-4]
        pop     rbp
        ret

code 4:
#include <stdio.h>
void printSquare(int num) {
    int result = num * num;
    printf("The square of %d is %d\n", num, result); //printf(format, num, result);
}
1st → EDI
2nd → ESI
3rd → EDX
asm code:
.LC0:
        .string "The square of %d is %d\n"
"printSquare":
        push    rbp
        mov     rbp, rsp
        sub     rsp, 32
        mov     DWORD PTR [rbp-20], edi
        mov     eax, DWORD PTR [rbp-20]
        imul    eax, eax
        mov     DWORD PTR [rbp-4], eax
        mov     edx, DWORD PTR [rbp-4]
        mov     eax, DWORD PTR [rbp-20]
        mov     esi, eax
        mov     edi, OFFSET FLAT:.LC0
        mov     eax, 0
        call    "printf"
        nop
        leave
        ret

code 5:
int calculate(int a, int b) {
    int x = a + b;
    int y = x * 2;
    return y - 3;
}
asm code:
"calculate":
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-20], edi
        mov     DWORD PTR [rbp-24], esi
        mov     edx, DWORD PTR [rbp-20]
        mov     eax, DWORD PTR [rbp-24]
        add     eax, edx
        mov     DWORD PTR [rbp-4], eax
        mov     eax, DWORD PTR [rbp-4]
        add     eax, eax
        mov     DWORD PTR [rbp-8], eax
        mov     eax, DWORD PTR [rbp-8]
        sub     eax, 3
        pop     rbp
        ret