{% load static theme_tags core_tags %}

<header class="header d-flex flex-wrap">
  {% render_utility_menu %}

  <a class="header__homepage-link mr-auto" href="/"><img alt="Logo" class="header__logo" src="{% static 'theme/img/logo.png' %}"></a>

  {% render_main_menu %}

  <div class="header__slide-menu-and-search d-flex d-xl-none justify-content-between">
    <div class="header__slide-menu slide-menu dropdown">
      <div class="slide-menu__opener dropdown-toggle" id="slide-menu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Menu <img alt="Main Menu" class="slide-menu__burger" src="{% static 'theme-v7.0/img/menu-burger.png' %}">
      </div>

      {% render_slide_menu %}
    </div>

    {% include 'theme-v7.0/main_menu/search.html' %}
  </div>
</header>
{% notification_all_pages %}
