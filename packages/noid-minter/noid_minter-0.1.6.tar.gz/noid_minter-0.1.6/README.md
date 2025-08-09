[noid minter](noid-minter)
===========

This is an [Archival Resource Key (ARK)](https://arks.org/about/) minter.
It is based on John A. Kunze's [Nice Opaque Identifiers (Noid)](https://legacy-n2t.n2t.net/e/noid.html)
software.


Usage
-----

```python
from noid_minter.minter import Minter

minter = Minter({"template": "xt7.reeedeeedk", "naan": "16417"})
the_ark = minter.mint().ark # e.g. 16417/xt74xg9f4v1p

dump = minter.to_json() # JSON string
minter2 = Minter.load(dump)
```


Design considerations
---------------------

The original Perl Noid provides a minter, binder, and resolver which share
a [BerkeleyDB](https://www.oracle.com/database/technologies/related/berkeleydb.html)
database for persistence. We reduce scope to the minter only and drop persistence,
providing `to_json()` and `load()` methods, with JSON as the transport language,
to allow clients to persist minters as they see fit.

Replayability of random minters is a particular concern. When Noid was first written,
it used Perl's `rand` for random numbers, which in turn relied on the random number
generator provided by the host system. On many Unix systems, this was
rand48, and in [Perl 5.19.4](https://metacpan.org/release/SHAY/perl-5.19.4/view/pod/perldelta.pod#rand_now_uses_a_consistent_random_number_generator),
the language standardized on rand48. We have chosen to use this PRNG to allow minter
databases that were created with Noid on Unix systems to be migrated to
noid-minter and mint new identifiers in a compatible, replayable manner.

The rand48 PRNG has known defects for pseudo-random number generation. However,
we are using it not for pseudo-randomness but first for uniform mixing of the sequence
of identifiers generated, so that two identifiers minted together are likely to be
quite different, and second for replayability of minting sequences, so that minters
can be migrated easily.

Users may want to bring their own PRNG to use with a minter. While support for other
PRNGs is not a current priority, we are opening to providing support for pluggable
PRNGs for minter. We welcome suggestions and code.


License
-------

Copyright (C) 2024-2025 MLE Slone. Licensed under the [MIT license](LICENSE.md).
