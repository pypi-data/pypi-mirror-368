# Zim-ID

Zim-ID is a Python library/API for validating, debugging, and generating Zimbabwean national ID numbers. It solves the bug in the [zwe](https://github.com/identique/idnumbers/tree/main/idnumbers/nationalid/zwe) module of the [idnumbers](https://github.com/identique/idnumbers) library where the **Modulus 23** algorithm was incorrectly implemented. The project has since been archived and is no longer maintained hence we couldn't contribute to fix the issue.

## Background
A valid Zimbabwean national ID number is one in the format `##-######L##` where:
- the **first two digits** represent the district code of the **registration office**,
- the **hyphen** is for formatting purposes,
- the **middle 6 or 7 digits** represent the sequential **national number**,
- the **alphabetical letter** represents the cryptographic **check letter**, and
- the **last two digits** represent the district code of the **district of origin**.

A check letter is one of 23 letters (26 of the English alphabet excluding I, O, and U) which is calculated as the letter at the index gotten by finding the remainder of dividing the resulting number from combining the registration office code and the national number by **23**. Hence the name **Modulus 23**.

## Installation

```bash
pip install zim_id
```

## Usage

### Validating ID numbers

This is a process of checking whether a given ID number is a valid Zimbabwean national ID number.

```python
ZimID.validate(id_number: str) -> bool:
````

#### Example Usage

```python
>>> from zim_id import ZimID
>>> id_number = "50-2001148W50"
>>> ZimID.validate(id_number)
>>> True
```

### Debugging ID numbers

This is a process of not only checking if a given ID number is a valid Zimbabwean national ID number, but also determining what's making it invalid. The debug method returns one of 6 integer flags:

```python
ZimID.debug(id_number: str) -> int:
```

| Flag | Meaning                                       |
|------|-----------------------------------------------|
| 0    | ID number is valid                            |
| 1    | ID number is incorrectly formatted            |
| 2    | ID number has unkown registration office code |
| 3    | ID number has unkown check letter             |
| 4    | ID number has unkown district of origin       |
| 5    | ID number has invalid check sum               |

#### Example

```python
>>> from zim_id import ZimID
>>> id_number = "50-2001148W50"
>>> ZimID.debug(id_number)
>>> 0
```

### Generating ID numbers

This is a process of generating random or custom valid Zimbabwean national ID numbers. The national number is always random although one can specify a custom registration office or district of origin.

> THE ID GENERATION FEATURE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE FEATURE OR ITS USE.

```python
ZimID.generate(reg_office: str | None, origin_district: str | None) -> str:
```

#### Example

```python
>>> from zim_id import ZimID

>>> ZimID.generate(None, None) # random reg_office, random origin_district
>>> '06-1522349S21'

>>> ZimID.generate("63", None) # custom reg_office, random origin_district
>>> '63-8158549W19'

>>> ZimID.generate(None, "08") # random reg_office, custom origin_district
>>> '07-8870909Y08'

>>> ZimID.generate("50", "50") # custom reg_office, custom origin_district
>>> '50-9924604Y50'
```

## Appendix

### District Codes

| District                          | Code |
|-----------------------------------|------|
| Beitbridge                        | 02   |
| Mberengwa                         | 03   |
| Bikita                            | 04   |
| Bindura                           | 05   |
| Binga                             | 06   |
| Buhera                            | 07   |
| Bulawayo                          | 08   |
| Mhondoro-Ngezi                    | 10   |
| Muzarabani                        | 11   |
| Chipinge                          | 13   |
| Chiredzi                          | 14   |
| Mazowe                            | 15   |
| Chikomba                          | 18   |
| Umzingwane                        | 19   |
| Insiza                            | 21   |
| Masvingo                          | 22   |
| Gokwe South                       | 23   |
| Kadoma                            | 24   |
| Goromonzi                         | 25   |
| Gokwe North                       | 26   |
| Gutu                              | 27   |
| Gwanda                            | 28   |
| Gweru                             | 29   |
| Chegutu                           | 32   |
| Nyanga                            | 34   |
| Bubi                              | 35   |
| Kariba                            | 37   |
| Hurungwe                          | 38   |
| Matobo                            | 39   |
| Lupane                            | 41   |
| Makoni                            | 42   |
| Marondera                         | 43   |
| Chimanimani                       | 44   |
| Mt. Darwin                        | 45   |
| Mbire                             | 46   |
| Murehwa                           | 47   |
| Mutoko                            | 48   |
| Mudzi                             | 49   |
| Mutasa                            | 50   |
| Nkayi                             | 53   |
| Mwenenzi                          | 54   |
| Bulilimamangwe                    | 56   |
| Kwekwe                            | 58   |
| Seke                              | 59   |
| Rushinga                          | 61   |
| Harare                            | 63   |
| Shurugwi                          | 66   |
| Zvishavane                        | 67   |
| Shamva                            | 68   |
| Makonde                           | 70   |
| Guruve                            | 71   |
| Tsholotsho                        | 73   |
| Mutare                            | 75   |
| Chirumanzu                        | 77   |
| Hwange                            | 79   |
| Hwedza                            | 80   |
| Zaka                              | 83   |
| Umguza                            | 84   |
| U.M.P. (Uzumba, Maramba, Pfungwe) | 85   |
| Zvimba                            | 86   |

**Note:** 00 is a valid district code of origin for foreigners.

## License
This project is licensed under the **MIT License** – see the [LICENSE](https://raw.githubusercontent.com/haripowesleyt/zim-id/main/LICENSE) file for details.
