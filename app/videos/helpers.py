from .. models import Purchase
from urllib.parse import urlparse, parse_qs
import re

def can_access_video(user:object, video:object) -> bool | bool | str:
    video_id = video.id
    user_id = user.id
    tutor_id = video.tutor.user_id
    owner = False

    #To check if the person is the tutor
    if (user_id == tutor_id):
        owner = True
        return True, owner, "Owner of the Video"
    if video.is_free:
        return True, owner, "Video Free"
    #To check if a student has paid
    if Purchase.query.filter_by(student_id=user_id, video_id=video_id).first():
        return True, owner, "Video Paid for"
    else:
        return False, owner, "Purchase required"


def extract_video_id(url: str) -> str:
    """Extracts the 11-character YouTube video ID from any standard YouTube URL style."""
    if not url:
        return None
        
    # Standardize the URL string
    url = url.strip()
    
    # 1. Handle regular expressions for quick matching (Shorts, Embeds, Shared links)
    regex_patterns = [
        r"youtu\.be/([^?&\s]+)",                  # Shortened URLs
        r"youtube\.com/embed/([^?&\s]+)",          # Embedded URLs
        r"youtube\.com/shorts/([^?&\s]+)",         # Shorts URLs
        r"youtube\.com/v/([^?&\s]+)"               # Legacy mobile URLs
    ]
    
    for pattern in regex_patterns:
        match = re.search(pattern, url)
        if match:
            youtube_video_id = match.group(1)[:11]
            return youtube_video_id # Return exactly the 11-character ID
            
    # 2. Handle standard watch URLs using robust URL parsing
    try:
        parsed_url = urlparse(url)
        if "youtube.com" in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0][:11]
    except Exception:
        pass
        
    return None

def recalculate_tutor_rating(video:object, db_object:object):
    #Calculate Total rating
    sum_rating = 0
    total_reviews = 0
    for v in video.tutor.videos:
        for review in v.reviews:
            total_reviews += 1
            sum_rating += int(review.rating)


    avg_rating = sum_rating/total_reviews

    video.tutor.avg_rating = avg_rating
    video.tutor.total_reviews = total_reviews
    #The Logic for the recalculating the student average is fundamentally flawed it will not scale properly
    # so there has to be a rewiring of the database to have a total reviews attachte to the tutor profile or then a separate ratings table attached to the tutor profile
    db_object.session.commit()

    