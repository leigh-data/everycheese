import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware

from everycheese.users.models import User
from ..models import Cheese
from ..views import (
    CheeseCreateView,
    CheeseListView,
    CheeseDetailView,
    CheeseUpdateView
)
from .factories import CheeseFactory

pytestmark = pytest.mark.django_db


def test_good_cheese_list_view_expanded(rf):
    url = reverse("cheeses:list")
    request = rf.get(url)
    response = CheeseListView.as_view()(request)
    assertContains(response, 'Cheese List')


def test_good_cheese_detail_view(rf, cheese):
    url = reverse("cheeses:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)
    response = CheeseListView.as_view()(request, slug=cheese.slug)
    assertContains(response, 'Cheese List')


def test_good_cheese_create_view(rf, admin_user, cheese):
    url = reverse("cheeses:add")
    request = rf.get(url)
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)
    assert response.status_code == 200


def test_cheese_list_contains_2_cheeses(rf):
    cheese1 = CheeseFactory()
    cheese2 = CheeseFactory()
    url = reverse('cheeses:list')
    request = rf.get(url)
    response = CheeseListView.as_view()(request)
    assertContains(response, cheese1.name)
    assertContains(response, cheese2.name)


def test_cheese_detail_contains_cheese_data(rf, cheese):
    url = reverse('cheeses:detail', kwargs={'slug': cheese.slug})
    request = rf.get(url)
    response = CheeseDetailView.as_view()(request, slug=cheese.slug)
    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)


def test_cheese_create_form_valid(rf, admin_user):
    url = reverse("cheeses:add")
    form_data = {
        "name": "Paski Sir",
        "description": "A salty hard cheese",
        "firmness": Cheese.Firmness.HARD
    }
    request = rf.post(url, form_data)
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)

    cheese = Cheese.objects.get(name="Paski Sir")

    assert cheese.description == "A salty hard cheese"
    assert cheese.firmness == Cheese.Firmness.HARD
    assert cheese.creator == admin_user


def test_good_cheese_update_view(rf, admin_user, cheese):
    url = reverse("cheeses:update", kwargs={'slug': cheese.slug})
    request = rf.get(url)
    request.user = admin_user
    response = CheeseUpdateView.as_view()(request, slug=cheese.slug)
    assertContains(response, "Update Cheese")


def test_cheese_update(rf, admin_user, cheese):
    """
    POST request to CheeseUpdateView updates a cheese and redirects
    """
    form_data = {
        'name': cheese.name,
        'description': 'Something new',
        'firmness': cheese.firmness
    }
    url = reverse("cheeses:update", kwargs={'slug': cheese.slug})
    request = rf.post(url, form_data)
    request.user = admin_user
    response = CheeseUpdateView.as_view()(request, slug=cheese.slug)

    # check that the cheese has beenchanged
    cheese.refresh_from_db()
    assert cheese.description == 'Something new'
