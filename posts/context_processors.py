def feed_curation_weights(request):
    """
    Captures incoming custom feed curation weights from URL parameters
    so the UI range sliders remain locked to the user's explicit preference.
    """
    return {
        'tech_weight': int(request.GET.get('tech', 50)),
        'art_weight': int(request.GET.get('art', 50)),
    }