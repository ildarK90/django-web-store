from django.views.generic import ListView, DetailView
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from market.models import LatestProducts
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.contrib.contenttypes.models import ContentType


class SmartphoneEdit(APIView):
    serializer_class = SmartPhoneDetailSerializer(partial=True)

    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self, pk):
        smartphone = SmartPhones.objects.all()
        print(smartphone)
        return Response(smartphone)

    def patch(self, request, pk, format=None):
        smartphone = SmartPhones.objects.get(pk=pk)
        serializer = SmartPhoneDetailSerializer(smartphone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            # return Response(SmartPhoneDetailSerializer(smartphone).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SmartUpdate(RetrieveUpdateDestroyAPIView):
    serializer_class = SmartPhoneDetailSerializer
    lookup_field = 'pk'
    queryset = SmartPhones.objects.all()


class NoteBookDetailed(APIView):
    """
    Выводим проект детально
    """
    serializer_class = NoteBookDetailSerializer

    def get_queryset(self, pk):
        notebook = NoteBook.objects.filter(pk=pk).first()
        print(notebook)
        return notebook

    # parser_classes = (MultiPartParser, FormParser,)

    def post(self, serializer):
        # serializer.save(photo=self.request.data.get('photo'))
        if serializer.is_valid:
            serializer.save()

    def patch(self, request, pk):
        # serializer.save(photo=self.request.data.get('photo'))
        notebook = NoteBook.objects.get(pk=pk)
        serializer = NoteBookDetailSerializer(notebook, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditCategory(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self):
        try:
            return Category.objects.all()
        except Category.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return Response({'status': 'Товар успешно удален'})















