rm -r build
python generate.py
python generate_dataframe.py
python generate_groupby.py
make html
cp source/.nojekyll build/html
# rm -r ../../muldataframe_doc2/*
# mv build/html/* ../../muldataframe_doc2/
