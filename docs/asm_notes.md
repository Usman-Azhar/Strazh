# x86 Assembly Notes
 
Ten simple C constructs, compiled on godbolt.org (x86-64, gcc, default flags),
mapped to the ASM shape each one produces. Goal: recognize these *shapes*
on sight by Day 9, not memorize exact syntax - compilers/flags will vary
the exact instructions, but the pattern stays the same.
 
---
 
## 1. Simple assignment
 
```c
int f1(void) {
    int y = 1;
    return y;
}
```
```asm
mov eax, 1      ; y=1 folded straight into the return register
ret
```
**Pattern:** trivial constants often get compiled directly into the
return-value register - no real "variable" exists in the output at all.
 
---
 
## 2. If statement (no else)
 
```c
int f2(int x) {
    int y = 0;
    if (x > 5) {
        y = 1;
    }
    return y;
}
```
```asm
mov eax, 0        ; y = 0 (default case)
cmp edi, 5        ; compare x against 5, sets flags only
jle .skip         ; jump on the INVERSE condition (x <= 5)
mov eax, 1        ; only runs if x > 5
.skip:
ret
```
**Pattern:** `cmp` + jump-on-inverse-condition. The `if` body is a block
that gets *skipped over*, not jumped into.
 
---
 
## 3. If / else
 
```c
int f3(int x) {
    int y;
    if (x > 5) {
        y = 1;
    } else {
        y = 2;
    }
    return y;
}
```
```asm
cmp edi, 5
jle .else_branch
mov eax, 1
jmp .done          ; must jump PAST the else branch after the if-branch runs
.else_branch:
mov eax, 2
.done:
ret
```
**Pattern:** same inverse-jump as #2, but now there's a second,
*unconditional* `jmp` at the end of the if-branch so it doesn't fall
through into the else-branch's code.
 
---
 
## 4. Else-if chain
 
```c
int f4(int x) {
    if (x == 0) return 10;
    else if (x == 1) return 20;
    else return 30;
}
```
```asm
cmp edi, 0
jne .check_one
mov eax, 10
ret
.check_one:
cmp edi, 1
jne .default_case
mov eax, 20
ret
.default_case:
mov eax, 30
ret
```
**Pattern:** each `else if` is just another `cmp` + conditional jump,
chained one after another - there's no special "else if" instruction,
it's if-statements nested inside the else of the previous one.
 
---
 
## 5. While loop
 
```c
int f5(int n) {
    int total = 0;
    while (n > 0) {
        total += n;
        n -= 1;
    }
    return total;
}
```
```asm
mov eax, 0
.loop_check:
cmp edi, 0
jle .loop_end      ; exit condition checked BEFORE body runs
add eax, edi
sub edi, 1
jmp .loop_check    ; unconditional jump back to re-check
.loop_end:
ret
```
**Pattern:** two jumps working together - one conditional (exit test),
one unconditional (repeat). Condition is tested before the first
iteration ever runs.
 
---
 
## 6. Do-while loop
 
```c
int f6(int n) {
    int total = 0;
    do {
        total += n;
        n -= 1;
    } while (n > 0);
    return total;
}
```
```asm
mov eax, 0
.loop_body:
add eax, edi
sub edi, 1
cmp edi, 0
jg .loop_body      ; jump back to TOP if condition still holds
ret
```
**Pattern:** compare to `while` above - the check happens AFTER the body,
and there's no separate entry-check jump, because a do-while always runs
at least once by definition.
 
---
 
## 7. For loop
 
```c
int f7(int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += i;
    }
    return total;
}
```
```asm
mov eax, 0         ; total = 0
mov ecx, 0         ; i = 0
.loop_check:
cmp ecx, edi        ; i < n ?
jge .loop_end
add eax, ecx        ; total += i
add ecx, 1          ; i++
jmp .loop_check
.loop_end:
ret
```
**Pattern:** identical skeleton to the `while` loop - a `for` is just
sugar for init + while + increment. If you can read #5, you can read
this.
 
---
 
## 8. Function call
 
```c
int add_one(int x) { return x + 1; }
int f8(int a) {
    return add_one(a);
}
```
```asm
; inside add_one:
add edi, 1
mov eax, edi
ret
 
; inside f8:
call add_one       ; pushes return address, jumps into add_one
ret                ; f8 returns whatever add_one left in eax
```
**Pattern:** `call` = push-return-address + jump. `ret` = pop that
address + jump back. Return values travel through `eax` by convention,
not through any variable name.
 
---
 
## 9. Function with local variables (stack frame)
 
```c
int f9(int a, int b) {
    int local1 = a + b;
    int local2 = a - b;
    return local1 * local2;
}
```
```asm
push rbp            ; save caller's base pointer (PROLOGUE)
mov rbp, rsp        ; establish our own stable frame
sub rsp, 16          ; reserve stack space for local1, local2
 
mov eax, edi
add eax, esi         ; local1 = a + b
mov [rbp-4], eax      ; store local1 on the stack
 
mov eax, edi
sub eax, esi         ; local2 = a - b
mov [rbp-8], eax      ; store local2 on the stack
 
mov eax, [rbp-4]
imul eax, [rbp-8]     ; local1 * local2
 
mov rsp, rbp         ; deallocate locals (EPILOGUE)
pop rbp              ; restore caller's base pointer
ret
```
**Pattern:** this is the prologue/epilogue mentioned in the roadmap -
`push rbp` / `mov rbp, rsp` at the start, mirrored by `mov rsp, rbp` /
`pop rbp` at the end. Local variables live at fixed negative offsets
from `rbp` (`[rbp-4]`, `[rbp-8]`), which is why `rbp` needs to stay
fixed for the whole function even while `rsp` moves around.
 
---
 
## 10. Array indexing
 
```c
int f10(int *arr, int i) {
    return arr[i];
}
```
```asm
mov eax, [rdi + rsi*4]   ; arr + (i * sizeof(int)) then dereference
ret
```
**Pattern:** `arr[i]` is never a "lookup" instruction - it's address
arithmetic (`base + index*element_size`) folded into a single memory
operand, then one dereference. This is the same base+offset math you
already did by hand computing RVA-to-offset conversions in the header
parsers, just running at instruction-decode speed instead of you doing
it with a calculator.
 
