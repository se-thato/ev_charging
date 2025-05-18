from django.shortcuts import render
from rest_framework.decorators import api_view
from .serializers import ProductSerializer
from .models import Product
from rest_framework.response import Response


#this function will allow to get the list of all products
# from the database
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# this will allow to get the details of a specific product by its id
@api_view(['GET'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    

#this function will allow to create a new product
@api_view(['POST'])
def product_create(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# this function will allow to update a product
@api_view(['PUT'])
def product_update(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    
# this function will allow to delete a product
# from the database
@api_view(['DELETE'])
def product_delete(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response(status=204)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)
    

