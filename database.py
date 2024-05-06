import random
import asyncio
import aiomysql
from datetime import datetime, timedelta
import config

async def add_user(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:    
        await cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
        if  (await cursor.fetchone()) is None:
            query = ("INSERT INTO users(user_id) VALUES(%s)")
            val = (user_id) 
            try: 
                await cursor.execute(query,val) 
                await conn.commit() 
            except Exception as ex: 
                print(ex)
                await conn.rollback() 
            
            return "succes create user"
        else:
            return "has alredy created"
        
async def change_name(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET name = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def change_college(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET college = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def change_age(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET age = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()

async def change_gender(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET gender = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def change_city(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET city = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def change_bio(user_id, text):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET description = %s WHERE user_id = %s")
        val = (text, user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def upload_file(user_id, file_id, file_type):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("INSERT INTO images (owner, file_id, file_type) VALUES (%s, %s, %s)")
        val = (user_id, file_id, file_type) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
async def check_count_files(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:   
        await cursor.execute(f"SELECT file_id FROM images WHERE owner = '{user_id}'")
        files_list = await cursor.fetchall()
        return len(files_list)