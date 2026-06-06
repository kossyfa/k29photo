# Images folder
Σε αυτόν τον φάκελο φορτώνουμε τις  φωτογραφίες πριν τρέξουμε το load_data.py
Τα αρχεία δεν ανεβαίνουν στο GitHub (.gitignore)

# Gitignore για τα jpg
echo "images/*.jpg" >> ~/k29photo/.gitignore
echo "images/*.png" >> ~/k29photo/.gitignore

# Commit
git add .
git commit -m "Add images folder, update load_data.py path"
git push
