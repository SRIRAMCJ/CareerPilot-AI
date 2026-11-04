from app.routers.gmail import classify_recruiter_message


def test_classifies_interview_and_assessment_updates():
    interview = classify_recruiter_message("Interview invitation", "Please share your availability for a technical round.")
    assessment = classify_recruiter_message("Online assessment", "Complete the coding test by Friday.")
    assert interview["category"] == "interview"
    assert interview["scheduling_hint"] is True
    assert assessment["category"] == "assessment"
    assert assessment["action_required"] is True


def test_classifies_offer_and_rejection_messages():
    offer = classify_recruiter_message("Offer letter", "We are pleased to offer you the role.")
    rejection = classify_recruiter_message("Application update", "Unfortunately we will not move forward.")
    assert offer["category"] == "offer"
    assert rejection["category"] == "rejection"
    assert rejection["action_required"] is False
