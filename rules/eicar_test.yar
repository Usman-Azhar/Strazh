rule EICAR_Test_String
{
    meta:
        description = "Detects the standard EICAR antivirus test string"
        author = "you"

    strings:
        // The official EICAR test string - a safe, industry-standard
        // string every AV vendor's engine is built to detect. Not malware.
        $eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

    condition:
        $eicar
}