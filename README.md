to run: 
$ export FLASK_APP=app.py
$ flask run

Navigate to:
http://127.0.0.1:5000/

Include relational diagram screenshot

Todo:  
~~1. Update Schema~~  
~~2. Allow user registrations~~  
~~3. Error handling of the user registration-- no duplicates~~  
~~4. Adding friends~~  
~~5. Show all friends~~  
~~6. Photo and album creation only after registration~~  
~~7. All visitor Photo and album browsing~~  
14. Both registered and anonymous users can leave comments. Users cannot leave comments for their own photos  
15. Liking a picture
8. Users can delete own albums and photos -- deleting album cascades to delete photos
8. Fix bug where blob isn't converted to image
    --> <li><img src='data:image/png;base64, {{photo[1]}}'/></li>
6. Top 10 user statistic page  
10. Tag your own particular photos and then search by them  
11. Search by tags for all photos  
12. View most popular tags  
13. multiple tag search
14. recommended photos (take 5 most commonly used tags and find photos that also have those tags)
15. recommended tags (take a tag or multiple as input, find the most common tags in other photos)
