# Day 22 - Isolated VM Setup

## Hypervisor

VirtualBox 7.x (free, CLI-scriptable via VBoxManage).

## Guest OS

Windows 10 Pro x64 (evaluation ISO from Microsoft).

## VM Configuration

| Setting          | Value                          | Why                                       |
|------------------|--------------------------------|-------------------------------------------|
| RAM              | 4 GB                           | Enough for most PE samples to run normally |
| CPU              | 2 cores                        | Lets multi-threaded samples behave naturally |
| Disk             | 60 GB dynamically allocated    | Room for Windows + dropped files           |
| Network adapter  | Host-only (vboxnet0)           | No internet from guest, host↔guest only    |
| Audio            | Disabled                       | Reduces attack surface, not needed          |
| USB              | Disabled                       | Same reason                                |
| Shared folders   | None                           | Isolation - files move via CAPE agent only  |

## Network: Why Host-Only?

- **NAT** would give the guest internet access - a live malware sample could phone
  home, download second-stage payloads, or exfiltrate data. Unacceptable.
- **Bridged** puts the guest on the real LAN - same problem, plus it exposes other
  machines on the network.
- **Host-only** creates an isolated virtual network between host and guest only.
  The guest can talk to the host (needed for CAPEv2's result server), but has
  zero internet access. This is the standard sandbox isolation model.

## Setup Steps

1. Create the host-only network adapter:
   ```
   VBoxManage hostonlyif create
   VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0
   ```

2. Create the VM:
   ```
   VBoxManage createvm --name "Strazh-Win10" --ostype Windows10_64 --register
   VBoxManage modifyvm "Strazh-Win10" --memory 4096 --cpus 2 --vram 128
   VBoxManage modifyvm "Strazh-Win10" --nic1 hostonly --hostonlyadapter1 vboxnet0
   VBoxManage modifyvm "Strazh-Win10" --audio-driver none --usb off
   ```

3. Create and attach disk:
   ```
   VBoxManage createmedium disk --filename "Strazh-Win10.vdi" --size 61440
   VBoxManage storagectl "Strazh-Win10" --name "SATA" --add sata
   VBoxManage storageattach "Strazh-Win10" --storagectl "SATA" --port 0 --type hdd --medium "Strazh-Win10.vdi"
   ```

4. Attach Windows ISO and install normally.

5. Inside the guest, set a static IP:
   ```
   IP:      192.168.56.101
   Mask:    255.255.255.0
   Gateway: (leave blank - no gateway = no internet)
   DNS:     (leave blank)
   ```

## Verification

From inside the guest:
```
ping 192.168.56.1        -> should succeed (host is reachable)
ping 8.8.8.8             -> should fail / timeout (no internet)
curl http://example.com   -> should fail (no internet)
```

From the host:
```
ping 192.168.56.101      -> should succeed (guest is reachable)
```

## Post-Install Guest Tweaks

- Disable Windows Update (no internet anyway, but prevents background noise)
- Disable Windows Defender real-time protection (it would interfere with sample execution)
- Disable screensaver and sleep (sample needs the desktop active)
- Install Python 3.10+ inside the guest (needed for the CAPE agent later)
