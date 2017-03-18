from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from django.db.models import Count, Sum
from rest_framework import viewsets, generics, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
import api.serializers as serializers
import main.models as models
import api.filters as filters
import api.lib.custom_filters as custom_filters


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = models.Restaurant.objects.all()
    serializer_class = serializers.Restaurant


class DishViewSet(viewsets.ModelViewSet):
    queryset = models.Dish.objects.all()
    serializer_class = serializers.Dish
    filter_class = filters.Dish

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if self.request.query_params.get('saved') == 'true':
            queryset = models.Dish.objects.filter(likes__user=self.request.user,
                                                  likes__did_like=True)
        else:
            queryset = self.filter_queryset(queryset.reduce_by_distance(
                location=request.query_params.get('from_location', '').split(','),
                meters=request.query_params.get('max_distance_meters', '')
            ).exclude(
                likes__did_like=False, updated__gte=(datetime.now() - timedelta(hours=9))
            ))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(convertedSet, many=True)
        return Response(serializer.data)


class RestaurantDishesViewSet(generics.ListAPIView):
    """
    Dishes from a particular restaurant

    Reference: http://stackoverflow.com/questions/17337843/how-to-implement-a-hierarchy-of-resources-eg-parents-id-children-in-django
    """
    queryset = models.Dish.objects.all()
    serializer_class = serializers.Dish
    filter_class = filters.Dish

    def get_queryset(self):
        rest_pk = self.kwargs['restaurant_pk']
        return self.queryset.filter(restaurant__pk=rest_pk)


class DeliveryProviderViewSet(viewsets.ModelViewSet):
    queryset = models.DeliveryProvider.objects.all()
    serializer_class = serializers.DeliveryProvider


class LikesList(APIView):
    """
    Post only, for saving likes

    * Requires token authentication.
    """
    def post(self, request, format=None):
        try:
            user = request.user
            did_like = request.data.get("did_like")
            dish = models.Dish.objects.get(pk=request.data.get("dish_id"))
            like = models.Like.objects.get(dish=dish, user=user)
            like.did_like = did_like
            like.save()
            return Response({"success": True, "created": False})
        except models.Like.DoesNotExist:
            like = models.Like(user=user, dish=dish, did_like=did_like)
            like.save()
            return Response({"success": True, "created": True})
        except models.Dish.DoesNotExist:
            return Response({"success": False, "created": False,
                             "Error": "Dish not found"}, 400)
