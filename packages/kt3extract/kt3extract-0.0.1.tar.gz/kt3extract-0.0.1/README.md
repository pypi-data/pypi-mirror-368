# Kill Team datacard extractor <!-- omit in toc -->

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-red?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Shop: Elecrow](https://img.shields.io/badge/shop-Elecrow-blue?style=flat-square)](https://www.elecrow.com/store/Binary-6)
[![Donations: Coffee](https://img.shields.io/badge/donations-Coffee-brown?style=flat-square)](https://github.com/Chrismettal#donations)
[![Version](https://img.shields.io/github/v/tag/chrismettal/kt3extract?label=version&style=flat-square)](https://https://github.com/Chrismettal/Kill-Team-datacard-extractor)

This is a script to extract Kill Team 3rd Edition datacards from the free rules PDFs published by Games Workshop.

The free PDFs always start with a few pages of unit rule datacards, followed by faction rule datacards. These are intended to be printed at home and cut out manually. This script automates the cutting part and outputs one image per card, or a stacked PDF with one page per card rotated to be oriented the same way.

**If you like my work please consider [supporting me](https://github.com/Chrismettal#donations)!**

## Table of contents <!-- omit in toc -->

- [Usage](#usage)
  - [Arguments](#arguments)
- [Todo](#todo)
- [Donations](#donations)
- [License](#license)

## Usage

- Go to [Warhammer-Community Kill Team downloads](https://www.warhammer-community.com/en-gb/downloads/kill-team/)
- Download the PDF for the Kill Team you want to play
- Take note of which pages have horizontally drawn datacards, and which pages have vertically drawn datacards.
  - (Unit cards are pasted as ~4 horizontal pages, while rule cards are pasted as ~6 vertical pages)
- Execute the script, making sure to set all required arguments

`kt3extract -h "1-3" -v "4-5" -o png -i /path/to/killteam.pdf`

### Arguments

All arguments are required.

- `-h` / `--horizontal`: Range of pages where horizontal datacards are situated. `-h "1-3"`
- `-v` / `--vertical`: Range of pages where vertical datacards are situated. `-h "4-5"`
- `-o` / `--output`: Format of output files. Allowed formats: `pdf`, `png`
- `-i` / `--input`: Path to your team's PDF file. `/path/to/killteam.pdf`

## Todo

- [x] Plausibility check input parameters, testing for range format
- [x] Plausibility check input path leads to a PDF
- [x] Read in PDF, splitting into two page stacks for horizontal and vertical pages
- [x] Cut and export each page stack
- [x] Export as stacked PDF
- [x] Add optional padding parameter
- [ ] Scale pages to be exactly 70mm x 120mm before padding
- [ ] Export as PNG

## Donations

**If you like my work please consider [supporting me](https://github.com/Chrismettal#donations)!**

## License

 <a rel="GPLlicense" href="https://www.gnu.org/licenses/gpl-3.0.html"><img alt="GPLv3" style="border-width:0" src="https://www.gnu.org/graphics/gplv3-or-later.png" /></a><br />This work is licensed under a <a rel="GPLlicense" href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPLv3 License</a>.
