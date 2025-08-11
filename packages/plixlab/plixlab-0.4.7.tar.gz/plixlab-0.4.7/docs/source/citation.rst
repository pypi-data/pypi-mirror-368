Citation
=========

Citations can be imported with the tag ``cite``


.. code-block:: python

  from plixlab import Slide

  Slide().cite('einstein1935',bibfile='biblio.bib').show()

.. import_example:: citation

| Multiple citations, which can be added using a list of keys, will be stacked vertically. If ``bibfile`` is not specified, the file ``~/.plix/biblio.bib`` will be used.


