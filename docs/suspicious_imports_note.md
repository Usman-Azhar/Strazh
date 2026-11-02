# Suspicious-adjacent imports (Day 17)

Observed in benign samples, flagged for later dynamic-analysis relevance.

## From notepad.exe (my own parser output)
- GetProcAddress (api-ms-win-core-libraryloader-l1-2-0.dll) — used here for
  ordinary dynamic function resolution, but this is the exact API malware
  uses to resolve dangerous functions by NAME at runtime specifically to
  avoid those function names appearing plainly in the static import table
  I just parsed. Same API, opposite intent.

## General notes
- WinExec — spawns a process without CreateProcess's fuller control; common
  in simple installers, also a lightweight way to launch a payload.
- VirtualAlloc / VirtualAllocEx — allocates memory with arbitrary protection
  flags (e.g. executable); legitimate for JIT/interpreters, also step 1 of
  shellcode injection.
- CreateRemoteThread — starts a thread inside *another* process; used by
  debuggers and some legitimate tooling, but the textbook process-injection API.
- WriteProcessMemory — writes bytes into another process's address space;
  pairs with CreateRemoteThread in classic injection chains.
- LoadLibraryA — dynamic DLL loading; used everywhere, but also how malware
  loads additional modules at runtime to evade static analysis.

None of these are malicious in isolation - they're normal OS primitives.
What matters is the *combination* and *context*, which static import
analysis alone can't see. That's what dynamic sandboxing (Track 3) is for.
