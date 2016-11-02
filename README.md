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
~~8. Users can delete own albums and photos~~
~~9. Liking a picture~~  
~~10. Both registered and anonymous users can leave comments. Users cannot leave comments for their own photos~~  
~~11. Top 10 user statistic page~~  
~~12. Tag your own particular photos and then 
~~13. Search by tags for all photos~~  
~~14. View most popular tags~~  
16. multiple tag search
15. recommended photos (take 5 most commonly used tags and find photos that also have those tags)
15. recommended tags (take a tag or multiple as input, find the most common tags in other photos)
9. test the delete function on comments and likes etc
16. test the stats page
17. test the tag ranking
14. Update tag click to show only users tags whereas tag search shows all users
8. Fix bug where blob isn't converted to image
    --> <li><img src='data:image/png;base64, {{photo[1]}}'/></li>
