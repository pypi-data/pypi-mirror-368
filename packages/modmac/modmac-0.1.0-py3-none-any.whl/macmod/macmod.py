import sys
import pyperclip


doc = """
This application accepts a MAC address in any format and returns it formatted in one of the standard styles.

Usage:
    mac <separator> <MAC>

Where:
    <separator> — one of '.', '-', ':'
    <MAC> — input MAC address in any common format

Returns:
    Formatted MAC address according to the specified separator.
    The formatted MAC address is also copied to the clipboard automatically.

Examples:

    > mac : 00-1A-2B-3C-4D-5E
    00:1A:2B:3C:4D:5E  (copied to clipboard)

    > mac - 001a.2b3c.4d5e
    00-1A-2B-3C-4D-5E  (copied to clipboard)

    > mac . 00-1A-2B-3C-4D-5E
    001a.2b3c.4d5e  (copied to clipboard)
"""

def main(*args):
    if len(args) != 2:
        print(doc)
        return
    sep, mac = args
    
    mac = clean_mac(mac)
    
    if sep == '-':
        formatted_mac = '-'.join(mac[i:i+2] for i in range(0, 12, 2))
        print(formatted_mac)
        pyperclip.copy(formatted_mac)
        sys.exit(0)
    
    if sep == ':':
        formatted_mac = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
        print(formatted_mac)
        pyperclip.copy(formatted_mac)
        sys.exit(0)

    if sep == '.':
        formatted_mac = '.'.join(mac[i:i+4] for i in range(0, 12, 4)).lower()
        print(formatted_mac)
        pyperclip.copy(formatted_mac)
        sys.exit(0)
    
    #Something went wrong
    print(doc)
    sys.exit(1)

def clean_mac(mac):
    allowed = set("0123456789abcdefABCDEF")
    mac = ''.join(c for c in mac if c in allowed).upper()
    if len(mac) != 12:
        print(doc)
        sys.exit(1)
    return mac

if __name__ == "__main__":
    main(*sys.argv[1:])
