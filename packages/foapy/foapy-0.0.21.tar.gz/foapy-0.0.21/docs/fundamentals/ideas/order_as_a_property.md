---
hide:
  - toc
---
# Order as a Property

Formal order analysis defines a special property of symbolic sequences - an Order.
The order is a sequence of natural numbers obtained from the original symbolic sequence by replacing each
of its elements with a natural number corresponding to the index of this element in the alphabet
sorted by the appearance of the elements in the original sequence [1, 2, 3].

The concept of an Order can be conveniently demonstrated using an example:


Let's assume there is a symbolic sequence

``` mermaid
block-beta
  columns 36
  s1["I"] s2["N"] s3["T"] s4["E"] s5["L"] s6["L"] s7["I"] s8["G"] s9["E"] s10["N"]
  s11["C"] s12["E"] s13[" "] s14["I"] s15["S"] s16[" "] s17["T"] s18["H"] s19["E"] s20[" "]
  s21["A"] s22["B"] s23["I"] s24["L"] s25["I"] s26["T"] s27["Y"] s28[" "] s29["T"] s30["O"]
  s31[" "] s32["A"] s33["D"] s34["A"] s35["P"] s36["T"]
```


Find and enumirate the first appearance of each element

``` mermaid
block-beta
  columns 36
  s1["I"] s2["N"] s3["T"] s4["E"] s5["L"] s6["L"] s7["I"] s8["G"] s9["E"] s10["N"]
  s11["C"] s12["E"] s13[" "] s14["I"] s15["S"] s16[" "] s17["T"] s18["H"] s19["E"] s20[" "]
  s21["A"] s22["B"] s23["I"] s24["L"] s25["I"] s26["T"] s27["Y"] s28[" "] s29["T"] s30["O"]
  s31[" "] s32["A"] s33["D"] s34["A"] s35["P"] s36["T"]

  space:36

  i1_1["1"] i2_1["2"] i3_1["3"] i4_1["4"] i5_1["5"] space:2 i6_1["6"] space:2 i7_1["7"] space
  i8_1["8"] space i9_1["9"] space:2 i10_1["10"] space:2
  i11_1["11"] i12_1["12"] space:4 i13_1["13"]
  space:2 i14_1["14"] space:2
  i15_1["15"] space i16_1["16"]

  classDef c1 fill:#ff7f0e,color:#fff;
  classDef c2 fill:#ffbb78,color:#000;
  classDef c3 fill:#2ca02c,color:#fff;
  classDef c4 fill:#98df8a,color:#000;
  classDef c5 fill:#d62728,color:#fff;
  classDef c6 fill:#ff9896,color:#000;
  classDef c7 fill:#9467bd,color:#fff;
  classDef c8 fill:#c5b0d5,color:#000;
  classDef c9 fill:#8c564b,color:#fff;
  classDef c10 fill:#c49c94,color:#000;
  classDef c11 fill:#e377c2,color:#fff;
  classDef c12 fill:#f7b6d2,color:#000;
  classDef c13 fill:#bcbd22,color:#fff;
  classDef c14 fill:#dbdb8d,color:#000;
  classDef c15 fill:#17becf,color:#fff;
  classDef c16 fill:#9edae5,color:#000;

  class s1,i1_1 c1
  class s2,i2_1 c2
  class s3,i3_1 c3
  class s4,i4_1 c4
  class s5,i5_1 c5
  class s8,i6_1 c6
  class s11,i7_1 c7
  class s13,i8_1 c8
  class s15,i9_1 c9
  class s18,i10_1 c10
  class s21,i11_1 c11
  class s22,i12_1 c12
  class s27,i13_1 c13
  class s30,i14_1 c14
  class s33,i15_1 c15
  class s35,i16_1 c16

  s1 --> i1_1
  s2 --> i2_1
  s3 --> i3_1
  s4 --> i4_1
  s5 --> i5_1
  s8 --> i6_1
  s11 --> i7_1
  s13 --> i8_1
  s15 --> i9_1
  s18 --> i10_1
  s21 --> i11_1
  s22 --> i12_1
  s27 --> i13_1
  s30 --> i14_1
  s33 --> i15_1
  s35 --> i16_1
```

The alphabet (with indexes) for the sequence would be sequence of unique elements:


``` mermaid
block-beta
  columns 16
  s1["I"] s2["N"] s3["T"] s4["E"] s5["L"] s8["G"]
  s11["C"] s13[" "] s15["S"] s18["H"]
  s21["A"] s22["B"] s27["Y"] s30["O"]
  s33["D"] s35["P"]

  space:16

  i1_1["1"] i2_1["2"] i3_1["3"] i4_1["4"] i5_1["5"] i6_1["6"] i7_1["7"]
  i8_1["8"] i9_1["9"] i10_1["10"]
  i11_1["11"] i12_1["12"] i13_1["13"]
  i14_1["14"]
  i15_1["15"] i16_1["16"]

  classDef c1 fill:#ff7f0e,color:#fff;
  classDef c2 fill:#ffbb78,color:#000;
  classDef c3 fill:#2ca02c,color:#fff;
  classDef c4 fill:#98df8a,color:#000;
  classDef c5 fill:#d62728,color:#fff;
  classDef c6 fill:#ff9896,color:#000;
  classDef c7 fill:#9467bd,color:#fff;
  classDef c8 fill:#c5b0d5,color:#000;
  classDef c9 fill:#8c564b,color:#fff;
  classDef c10 fill:#c49c94,color:#000;
  classDef c11 fill:#e377c2,color:#fff;
  classDef c12 fill:#f7b6d2,color:#000;
  classDef c13 fill:#bcbd22,color:#fff;
  classDef c14 fill:#dbdb8d,color:#000;
  classDef c15 fill:#17becf,color:#fff;
  classDef c16 fill:#9edae5,color:#000;

  class s1,i1_1 c1
  class s2,i2_1 c2
  class s3,i3_1 c3
  class s4,i4_1 c4
  class s5,i5_1 c5
  class s8,i6_1 c6
  class s11,i7_1 c7
  class s13,i8_1 c8
  class s15,i9_1 c9
  class s18,i10_1 c10
  class s21,i11_1 c11
  class s22,i12_1 c12
  class s27,i13_1 c13
  class s30,i14_1 c14
  class s33,i15_1 c15
  class s35,i16_1 c16

  s1 --> i1_1
  s2 --> i2_1
  s3 --> i3_1
  s4 --> i4_1
  s5 --> i5_1
  s8 --> i6_1
  s11 --> i7_1
  s13 --> i8_1
  s15 --> i9_1
  s18 --> i10_1
  s21 --> i11_1
  s22 --> i12_1
  s27 --> i13_1
  s30 --> i14_1
  s33 --> i15_1
  s35 --> i16_1

  i1_1 --> s1
  i2_1 --> s2
  i3_1 --> s3
  i4_1 --> s4
  i5_1 --> s5
  i6_1 --> s8
  i7_1 --> s11
  i8_1 --> s13
  i9_1 --> s15
  i10_1 --> s18
  i11_1 --> s21
  i12_1 --> s22
  i13_1 --> s27
  i14_1 --> s30
  i15_1 --> s33
  i16_1 --> s35
```


Determine the order of the sequence by replacing each element of the sequence with its corresponding alphabet index

``` mermaid
block-beta
  columns 36
  s1["I"] s2["N"] s3["T"] s4["E"] s5["L"] s6["L"] s7["I"] s8["G"] s9["E"] s10["N"]
  s11["C"] s12["E"] s13[" "] s14["I"] s15["S"] s16[" "] s17["T"] s18["H"] s19["E"] s20[" "]
  s21["A"] s22["B"] s23["I"] s24["L"] s25["I"] s26["T"] s27["Y"] s28[" "] s29["T"] s30["O"]
  s31[" "] s32["A"] s33["D"] s34["A"] s35["P"] s36["T"]

  space:36

  i1_1["1"] i2_1["2"] i3_1["3"] i4_1["4"] i5_1["5"] i5_2["5"] i1_2["1"] i6_1["6"] i4_2["4"] i2_2["2"] i7_1["7"] i4_3["4"]
  i8_1["8"] i1_3["1"] i9_1["9"] i8_2["8"] i3_2["3"] i10_1["10"] i4_4["4"] i8_3["8"]
  i11_1["11"] i12_1["12"] i1_4["1"] i5_3["5"] i1_5["1"] i3_3["3"] i13_1["13"]
  i8_4["8"] i3_4["3"] i14_1["14"] i8_5["8"] i11_2["11"]
  i15_1["15"] i11_3["11"] i16_1["16"] i3_5["3"]

  classDef c1 fill:#ff7f0e,color:#fff;
  classDef c2 fill:#ffbb78,color:#000;
  classDef c3 fill:#2ca02c,color:#fff;
  classDef c4 fill:#98df8a,color:#000;
  classDef c5 fill:#d62728,color:#fff;
  classDef c6 fill:#ff9896,color:#000;
  classDef c7 fill:#9467bd,color:#fff;
  classDef c8 fill:#c5b0d5,color:#000;
  classDef c9 fill:#8c564b,color:#fff;
  classDef c10 fill:#c49c94,color:#000;
  classDef c11 fill:#e377c2,color:#fff;
  classDef c12 fill:#f7b6d2,color:#000;
  classDef c13 fill:#bcbd22,color:#fff;
  classDef c14 fill:#dbdb8d,color:#000;
  classDef c15 fill:#17becf,color:#fff;
  classDef c16 fill:#9edae5,color:#000;

  class s1,s7,s14,s23,s25,i1_1,i1_2,i1_3,i1_4,i1_5 c1
  class s2,s10,i2_1,i2_2 c2
  class s3,s17,s26,s29,s36,i3_1,i3_2,i3_3,i3_4,i3_5 c3
  class s4,s9,s12,s19,i4_1,i4_2,i4_3,i4_4 c4
  class s5,s6,s24,i5_1,i5_2,i5_3 c5
  class s8,i6_1 c6
  class s11,i7_1 c7
  class s13,s16,s20,s28,s31,i8_1,i8_2,i8_3,i8_4,i8_5 c8
  class s15,i9_1 c9
  class s18,i10_1 c10
  class s21,s32,s34,i11_1,i11_2,i11_3 c11
  class s22,i12_1 c12
  class s27,i13_1 c13
  class s30,i14_1 c14
  class s33,i15_1 c15
  class s35,i16_1 c16


  s1 --> i1_1
  s7 --> i1_2
  s14 --> i1_3
  s23 --> i1_4
  s25 --> i1_5

  s2 --> i2_1
  s10 --> i2_2

  s3 --> i3_1
  s17 --> i3_2
  s26 --> i3_3
  s29 --> i3_4
  s36 --> i3_5

  s4 --> i4_1
  s9 --> i4_2
  s12 --> i4_3
  s19--> i4_4

  s5 --> i5_1
  s6 --> i5_2
  s24 --> i5_3

  s8 --> i6_1

  s11 --> i7_1

  s13 --> i8_1
  s16 --> i8_2
  s20 --> i8_3
  s28 --> i8_4
  s31 --> i8_5

  s15 --> i9_1
  s18 --> i10_1

  s21 --> i11_1
  s32 --> i11_2
  s34 --> i11_3

  s22 --> i12_1
  s27 --> i13_1
  s30 --> i14_1
  s33 --> i15_1
  s35 --> i16_1
```


The order of symbolic sequence `INTELLIGENCE IS THE ABILITY TO ADAPT` is

``` mermaid
block-beta
  columns 36
  i1_1["1"] i2_1["2"] i3_1["3"] i4_1["4"] i5_1["5"] i5_2["5"] i1_2["1"] i6_1["6"] i4_2["4"] i2_2["2"] i7_1["7"] i4_3["4"]
  i8_1["8"] i1_3["1"] i9_1["9"] i8_2["8"] i3_2["3"] i10_1["10"] i4_4["4"] i8_3["8"]
  i11_1["11"] i12_1["12"] i1_4["1"] i5_3["5"] i1_5["1"] i3_3["3"] i13_1["13"]
  i8_4["8"] i3_4["3"] i14_1["14"] i8_5["8"] i11_2["11"]
  i15_1["15"] i11_3["11"] i16_1["16"] i3_5["3"]
```

Despite the triviality of the concept Order, it allows us to separate the elements and composition of a sequence and to define the compositional equivalence of different sequences.

Example of sequences with equals orders:

```pyodide exec="on" install="foapy,numpy"
import foapy
import numpy as np

seqA = list("INTELLIGENCE IS THE ABILITY TO ADAPT TO CHANGE")
seqB = list("1N73LL1G3NC321527H324B1L17Y27024D4P72702CH4NG3")
orderA = foapy.order(seqA)
orderB = foapy.order(seqB)
print("SeqA and SeqB orders are equals -", np.all(orderA == orderB))
print("Order =", orderA)
```

<style>
.md-typeset table:not([class]) th {
    min-width: 0 !important;
}

.md-typeset td:not([class]):not(:last-child), .md-typeset th:not([class]):not(:last-child) {
    border-right: .05rem solid var(--md-typeset-table-color);
}

.md-typeset td, .md-typeset th {
    padding-left: 0.4em !important;
    padding-right: 0.4em !important;
    padding-top: 0.1em !important;
    padding-bottom: 0.1em !important;
    text-align: center !important;
}
</style>

# References:

1. Curtis Cooper and Robert E. Kennedy. 1992. Patterns, automata, and Stirling numbers of the second kind. Math. Comput. Educ. 26, 2 (Spring 1992), 120–124.
2. Gumenjuk A., Kostyshin A., Simonova S. An approach to the research of the structure of linguistic and musical texts. Glottometrics. 2002. № 3. P. 61–89.
3. (In russian) V.I. Arnold, Complexity of finite sequences of zeros and ones and geometry of finite function spaces: el. print, 2005. http://mms.mathnet.ru/meetings/2005/arnold.pdf
