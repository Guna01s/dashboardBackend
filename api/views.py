from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import mysql.connector as sql 
from .models import Users
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required

# from rest_framework import generics
from .models import UserProfile
from .models import deviceStatus
from .serializers import UserProfileSerializer

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from mysql.connector.pooling import PooledMySQLConnection ,MySQLConnection
from typing import Any 


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    name = request.data.get('name')
    email = request.data.get('email')
    password = request.data.get('password')

    if not name or not email or not password:
        return Response({'error': 'Please provide a name, email, and password.', 'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    db = sql.connect(host="localhost", user="root", passwd="root", database='users_database_api')
    cursor = db.cursor()

    check_query = "SELECT * FROM users_database_api WHERE email = %s"
    cursor.execute(check_query, (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        db.close()
        return Response({'error': 'Email already exists. Please choose a different email.', 'status_code': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    insert_query = "INSERT INTO users_database_api (name, email, password) VALUES (%s, %s, %s)"
    values = (name, email, password)
    cursor.execute(insert_query, values)

    db.commit()
    db.close()

    return Response({'message': 'User registered successfully.', 'status_code': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # Connect to the MySQL database
    db = sql.connect(host="localhost", user="root", passwd="root", database='users_database_api')
    cursor = db.cursor()

    select_query = "SELECT * FROM users_database_api WHERE email=%s AND password=%s"
    values = (email, password)
    cursor.execute(select_query, [email,password])

    result = cursor.fetchall()

    db.close()

    if result:
        return Response({'message': 'Login successful.', 'status_code': status.HTTP_200_OK}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials.', 'status_code': status.HTTP_401_UNAUTHORIZED}, status=status.HTTP_401_UNAUTHORIZED)

from .serializers import UserProfileSerializer

## dummy
class ToggleSwitchAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.toggle_switch = not user_profile.toggle_switch
        user_profile.save()
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

## connect to MySqlCommentLine
from mysql.connector import pooling

def get_database_connection() -> PooledMySQLConnection:
    db_config = {
        'user': 'root',
        'password': 'root',
        'host': 'localhost',
        'database': 'users_database_api',
    }

    connection_pool = pooling.MySQLConnectionPool(pool_name='mypool', pool_size=5, **db_config)
    connection = connection_pool.get_connection()

    return connection

## try

@api_view(['POST'])
@permission_classes([AllowAny])
def saveToggle(request):
    # ...

    try:
        deviceStat = request.data.get('deviceStat')

        db: MySQLConnection | Any = get_database_connection()

        cursor = db.cursor()
        insert_query = "INSERT INTO toggle_table (deviceStat) VALUES (%s)"
        values = (deviceStat,)  # Note the comma to create a tuple
        cursor.execute(insert_query, values)

        db.commit()
        return Response({'status': 'success'})

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})

    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

