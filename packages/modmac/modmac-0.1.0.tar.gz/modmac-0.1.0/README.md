# modmac

A simple command-line tool to format MAC addresses in standard styles.

## Features

- Accepts MAC addresses in any common format.
- Outputs formatted MAC using `:`, `-`, or `.` separators.
- Copies the formatted MAC to the clipboard automatically.

## Usage

```
mac <separator> <MAC>
```

Where:

<separator> — one of .-:

<MAC> — input MAC address

Examples
```
> mac : 00-1A-2B-3C-4D-5E
00:1A:2B:3C:4D:5E  (copied to clipboard)

> mac - 001a.2b3c.4d5e
00-1A-2B-3C-4D-5E  (copied to clipboard)

> mac . 00-1A-2B-3C-4D-5E
001a.2b3c.4d5e  (copied to clipboard)

```