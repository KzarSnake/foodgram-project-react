from collections import Counter

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from users.models import CustomUser

from .filters import IngredientSearchFilter, RecipeSearchFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscribeSerializer,
    TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы c пользователем и подписки на авторов."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                Subscribe.objects.create(user=request.user, author=author),
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Subscribe.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=('get',), permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тэгами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeSearchFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create_instance(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_instance(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_instance(Favorite, request.user, pk)
        return self.delete_instance(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_instance(ShoppingCart, request.user, pk)
        return self.delete_instance(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, user):
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=user.user
        )
        compressed_ingredients = Counter()
        for ing in ingredients:
            compressed_ingredients[
                (ing.ingredient.name, ing.ingredient.measurement_unit)
            ] += ing.amount
        shopping_list = [
            f"- {name}: {amount} {measurement_unit}\n"
            for (
                name,
                measurement_unit,
            ), amount in compressed_ingredients.items()
        ]
        filename = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
