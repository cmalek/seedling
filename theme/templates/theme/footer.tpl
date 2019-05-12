{% load static core_tags theme_70_menu_tags %}

{% with request.site.settings as settings %}
  <footer class="footer d-flex flex-column flex-wrap flex-sm-row justify-content-sm-between">
    {# These two sit on top of the each other in the footer. They're not decendants because it made the CSS easier. #}
    <div class="footer__torch-box"></div>
    <img alt="Caltech Torch" class="footer__torch" src="{% static 'theme-v7.0/img/flame.png' %}">

    <div class="footer__left">
      <img alt="Caltech Logo" class="footer__left__caltech-wordmark" src="{% static 'core/img/caltech-new-logo.png' %}">
      <div class="footer__left__caltech-title">California Institute of Technology</div>
    </div>

    <div class="footer__right">
      <img class="footer__right__map-marker" src="{% static 'theme-v7.0/img/icon-footerpin.png' %}" alt="map marker">
      <div class="footer__right__contact-info-row">1200 East California Boulevard</div>
      <div class="footer__right__contact-info-row">Pasadena, California 91125</div>
    </div>

    {% render_footer_menu %}
  </footer>
{% endwith %}
