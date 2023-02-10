# Scoring

Here you can find details on how scoring function works.

The scoring function consists of seven scores:
* Lemmatization score (`lemma` tag),
* POS score (`UPOS` tag), $\large^{\*}$
* Grammatical features score (`feats` tag),
* UAS (`heads` tag),
* LAS (`deprel` tag),
* Semantic slot score (`semslot` tag),
* Semantic class score (`semclass` tag).

First three subfunctions can be grouped into **morphology** scoring, UAS and LAS are known to be a **syntax** scores, and last two are a **semantic** scoring group.

$\large^{\*}$ - Note that `XPOS` tag is ignored, for it's always an empty filed (`_`) in SEMarkup. We therefore use term POS instead of UPOS for convenience.

## Morphology

### Lemmatization

Lemmatization score is a weighted true-false classification, which can be expressed as follows:

$$\large
ScoreLemma(test, gold) = LemmaWeight(gold_{POS}) * \[Normalize(test_{lemma}) = Normalize(gold_{lemma})\],
$$

where $LemmaWeight$ is defined at [weights_estimator](weights_estimator/README.md#lemma), and $\[x = y\]$ is [Iverson bracket notation](https://en.wikipedia.org/wiki/Iverson_bracket).

Function $Normalize$ makes input lowercase and replaces letter `ё` with letter `е`. So, $\[Normalize(\text{Ёжик}) = Normalize(\text{ежик})\]$ is $1$.

### POS

Part-of-speech score is a simple true-false classification, expressed as:

$$\large
ScorePOS(test, gold) = \[test_{POS} = gold_{POS}\].
$$

### Grammatical features

Grammatical features score is a weighted mean of grammatical features with a penalty, i.e.:

$$\large
ScoreFeats(test, gold) = 
Penalty(test_{feats}, gold_{feats}) * 
\frac{
    \sum_{Cat\ \in\ gold_{feats}} FeatsWeight(Cat) * \[test_{feats}^{Cat} = gold_{feats}^{Cat}\] }{
    \sum_{Cat\ \in\ gold_{feats}} FeatsWeight(Cat) },
$$

where

$$\large
Penalty(x, y) =
\begin{cases}
    \frac{ 1 }{ 1 + (Length(x) - Length(y)) } & \text{if } Length(x) > Length(y), \\
     1 & \text{otherwise},
\end{cases}
$$

$FeatsWeight$ can be found at [weights_estimator](weights_estimator/README.md#grammatical-features),

and $\[test_{feats}^{Cat} = gold_{feats}^{Cat}\]$ implies $1$ if and only if grammatical category $Cat$ is present in both $test_{feats}$ and $test_{feats}$ and their corresponding grammemes of this category are equal. For example, let's say \
$\large test_{feats} =$ `Animacy=Inan|Case=Loc|Gender=Neut|Number=Sing` and \
$\large gold_{feats} =$ `Case=Nom|Degree=Pos|Gender=Fem|Number=Sing`. \
Then \
$\large \[test_{feats}^{Case} = gold_{feats}^{Case}\]$ is 0, since `Loc` and `Nom` grammemes are not equal, \
$\large \[test_{feats}^{Degree} = gold_{feats}^{Degree}\]$ is 0, since test features do not have `Degree` category, \
$\large \[test_{feats}^{Gender} = gold_{feats}^{Gender}\]$ is 0, since `Neut` and `Fem` grammemes are not equal, \
$\large \[test_{feats}^{Number} = gold_{feats}^{Number}\]$ is 1, since test features have `Number` category and its grammeme is equal to the gold one.

As for penalty formula, it lowers the score if test is longer than gold.
If there were no penalty, one could simply predict all grammatical categories existing per each token, and score would not get any worse (because the rightmost part of the ScoreFeats does not penalize overlength). It's not what we expect from a good morphology classifier, so that's why we add penalty here.

## Syntax

### UAS

Unlabeled Attachment Score is a simple true-false classification:

$$\large
UAS(test, gold) = \[test_{head} = gold_{head}\].
$$

### LAS

Labeled Attachment Score is a true-false classification, also conditioned on `head` tags' equality:

$$\large
LAS(test, gold) = \[test_{head} = gold_{head}\] * \[test_{deprel} = gold_{deprel}\].
$$

## Semantic

### Semantic slot

Semantic slot score is a simple true-false classification:

$$\large
ScoreSemslot(test, gold) = \[test_{semslot} = gold_{semslot}\].
$$

<!-- Any insights on `head` relations from other perticipants, maybe?.. -->

### Semantic class

Semantic class score is calculated based on taxonomy of semantic classes. _Taxonomy of semantic classes_ is a forest (set of trees), where each node represents a semantic class, and any of its children is a more specific semantic (sub)class. For example, `CANINAE` node has `DOG`, `WOLF`, `FOX`, `JACKAL`, `DINGO` and `COYOTE` children.

The very score looks as follows:

$$\large
ScoreSemclass(test, gold) = \frac{ 1 }{ 1 + Distance(test_{semclass}, gold_{semclass}) },
$$

where

$$\large
Distance(u, v) =
\begin{cases}
     PathLength(u, v) & \text{if $u$ and $v$ in one tree}, \\
     \infty & \text{if $u$ and $v$ in different trees}.
\end{cases}
$$

That is, the further test and gold semantic classes are in taxonomy, the lower the score is. If classes are in different trees, the score is zero.

Also, for whose who wonder how $PathLength$ is calculated:

$$\large PathLength(u, v) = Depth(u) - Depth(LCA(u, v)) + Depth(v) - Depth(LCA(u, v)),$$

where $LCA(u, v)$ is a lowest common ancestor of $u$ and $v$.

## Averaging

Note that some scores ( $ScoreLemma$ , for instance) are strictly less than one, which means the score of ideal parsing is also less than one. To account for this issue, we tweak the averaging in a following manner:

$$\large
AverageScoreX(tests, golds) = \frac{ \sum_{(test,\ gold)\ \in\ (tests,\ golds)} ScoreX(test, gold) }{ \sum_{gold\ \in\ golds} ScoreX(gold, gold) },
$$

where $ScoreX$ is any of the scores listed above.
