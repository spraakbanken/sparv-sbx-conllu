# Multiword

[**Tracking issue**](https://github.com/spraakbanken/sparv-sbx-conllu/issues/15)

`sparv-sbx-conllu` does not handle CoNLL-U:s multiword (id is a span, e.g. `15-16`) tokens fully, since `Sparv` has no way to
represent a token that is not present in the text.

`sparv-sbx-conllu` currently handles multiword tokens as follows:

- Take `form` and `misc` from the multiword token.
- Take `lemma`, `upos`, `xpos`, `head`, `deprel` and `deps` from the subtokens that is the root of the deprel subtree.
- Gives the merged token the id of the root of the subtree.

This way the dependency tree of a sentence is mostly intact (at least a tree), see examples below.

## Example `en_ewt-ud-test`

From the example file [`en_ewt-ud-test_excerp.conllu`](../assets/texts/en_ewt-ud-test_excerp.conllu)
we can see the diff against the original deptree (`-`) and `sparv-sbx-conllu`:s deptree (`+`).

```diff
--- assets/en_ewt-ud-test/en_ewt-ud-test_excerp_export.gold.deptree	2025-12-02 13:10:59.862987388 +0100
+++ en_ewt-ud-test_excerp.deptree	2025-12-02 13:21:59.924288744 +0100
@@ -78,23 +78,20 @@
     (deprel:ccomp) form:backfire lemma:backfire upos:VERB [12]
         (deprel:mark) form:that lemma:that upos:SCONJ [5]
         (deprel:nsubj) form:rush lemma:rush upos:NOUN [8]
-            (deprel:nmod:poss) form:Google lemma:Google upos:PROPN [6]
-                (deprel:case) form:'s lemma:'s upos:PART [7]
+            (deprel:nmod:poss) form:Google's lemma:Google upos:PROPN [6]
             (deprel:nmod) form:ubiquity lemma:ubiquity upos:NOUN [10]
                 (deprel:case) form:toward lemma:toward upos:ADP [9]
         (deprel:aux) form:might lemma:might upos:AUX [11]
         (deprel:advcl:relcl) form:heard lemma:hear upos:VERB [18]
             (deprel:punct) form:-- lemma:-- upos:PUNCT [13]
             (deprel:obj) form:which lemma:which upos:PRON [14]
-            (deprel:nsubj) form:we lemma:we upos:PRON [15]
-            (deprel:aux) form:'ve lemma:have upos:AUX [16]
+            (deprel:nsubj) form:we've lemma:we upos:PRON [15]
             (deprel:advmod) form:all lemma:all upos:ADV [17]
             (deprel:advmod) form:before lemma:before upos:ADV [19]
     (deprel:conj) form:put lemma:put upos:VERB [27]
         (deprel:punct) form:, lemma:, upos:PUNCT [20]
         (deprel:cc) form:but lemma:but upos:CCONJ [21]
-        (deprel:nsubj:pass) form:it lemma:it upos:PRON [22]
-        (deprel:aux:pass) form:'s lemma:be upos:AUX [23]
+        (deprel:nsubj:pass) form:it's lemma:it upos:PRON [22]
         (deprel:advmod) form:particularly lemma:particularly upos:ADV [24]
         (deprel:advmod) form:well lemma:well upos:ADV [25]
             (deprel:punct) form:- lemma:- upos:PUNCT [26]
@@ -141,8 +138,7 @@

 {'sent_id': 'weblog-blogspot.com_marketview_20050511222700_ENG_20050511_222700-0007'}
 (deprel:root) form:staying lemma:stay upos:VERB [3]
-    (deprel:nsubj) form:I lemma:I upos:PRON [1]
-    (deprel:aux) form:'m lemma:be upos:AUX [2]
+    (deprel:nsubj) form:I'm lemma:I upos:PRON [1]
     (deprel:advmod) form:away lemma:away upos:ADV [4]
         (deprel:obl) form:stock lemma:stock upos:NOUN [7]
             (deprel:case) form:from lemma:from upos:ADP [5]
```

## Example `sentence-comments`

From the example file [`sentence-comments.conllu`](../assets/texts/sentence-comments.conllu)
we can see the diff against the original deptree (`-`) and `sparv-sbx-conllu`:s deptree (`+`).

```diff
--- assets/sentence-comments/sentence-comments_export.gold.deptree	2025-12-02 13:10:59.863489261 +0100
+++ sentence-comments.deptree	2025-12-02 13:37:30.953120112 +0100
@@ -14,8 +14,7 @@
     (deprel:punct) form:. lemma:. upos:PUNCT [5]

 {'sent_id': 'panc0.s4'}
-(deprel:root) form:अनुश्रूयते lemma:अनु-श्रु upos:VERB [3]
+(deprel:root) form:यथानुश्रूयते lemma:अनु-श्रु upos:VERB [3]
     (deprel:nsubj) form:तत् lemma:तद् upos:DET [1]
-    (deprel:advmod) form:यथा lemma:यथा upos:ADV [2]
     (deprel:punct) form:। lemma:। upos:PUNCT [4]
```
