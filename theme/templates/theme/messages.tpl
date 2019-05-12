{% if messages %}
  <ul class="messages">
    {% for message in messages %}
      <li class="{{ message.tags }}">
        {% if 'safe' in message.tags %}
          {{ message | safe | linebreaksbr }}
        {% else %}
          {{ message | linebreaksbr }}
        {% endif %}
      </li>
    {% endfor %}
  </ul>
{% endif %}
