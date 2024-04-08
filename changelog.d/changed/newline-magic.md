- Changed the way newlines are handled for fragments. Newlines surrounding
  fragments are now significant when concatenation of fragments happens.
  However, a _lack_ of final is considered an error, and one is always added.
  The foremost consequence of this change is that list items now concatenate
  without a blank line between them.
