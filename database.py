import random
import asyncio
import aiomysql
from datetime import datetime, timedelta
import config

async def add_user(user_id, username):
    try:
        conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
        async with conn.cursor(aiomysql.DictCursor) as cursor:    
            await cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
            if  (await cursor.fetchone()) is None:
                query = ("INSERT INTO users(user_id, username) VALUES(%s, %s)")
                val = (user_id, username) 
                try: 
                    await cursor.execute(query,val) 
                    await conn.commit() 
                except Exception as ex: 
                    print(ex)
                    await conn.rollback() 
                
                return "succes create user"
            else:
                return "has alredy created"
    except:
        print('ошибка')
        
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
    
async def save_anket(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("UPDATE users SET state = 1 WHERE user_id = %s")
        val = (user_id) 
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
    
async def delete_images(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("DELETE FROM images WHERE owner = %s")
        val = (user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()      
        return await cursor.fetchall()
    
async def delete_anket(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:  
        query = ("DELETE FROM users WHERE user_id = %s")
        val = (user_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()       
        query = ("DELETE FROM images WHERE owner = %s")
        val = (user_id) 
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
    
async def get_anket(user_id):
    user_id = int(user_id)
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:   
        await cursor.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'")
        user = await cursor.fetchone()
        await cursor.execute(f"SELECT * FROM images WHERE owner = '{user_id}'")
        images = await cursor.fetchall()
        return {'user': user, 'images' : images}
    
async def get_random_anket(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:   
        await cursor.execute(f"SELECT * FROM views WHERE first_id = '{user_id}' AND date_view >= CURDATE()")
        list_direct = []
        list_users = []
        req = await cursor.fetchall()
        print(req)
        for i in req:
            list_direct.append(i['direct_id'])

        await cursor.execute(f"SELECT user_id FROM users WHERE state = 1")
        for i in (await cursor.fetchall()):
            list_users.append(i['user_id'])
        
        try:
            list_users.remove(str(user_id))
        except:
            pass
        result = list(set(list_users) - set(list_direct))
        print("Список пользователей ",list_users)
        print("Список пользователей которых мы просмотрели ",list_direct)
        print("Конечный список", result)
        return_result = ''
        if len(result) == 0:
            return None
        else:
            return_result = random.choice(result)
            # conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
            # async with conn.cursor(aiomysql.DictCursor) as cursor:  
            query = ("INSERT INTO views (first_id, direct_id) VALUES (%s, %s)")
            val = (user_id, return_result) 
            try:
                await cursor.execute(query,val) 
                await conn.commit() 
            except Exception as ex: 
                print('Ошибка ',ex)
                await conn.rollback()    
            # else:
            #     await cursor.execute(f"SELECT * FROM users ORDER BY RAND() LIMIT 1")
            #     anket = await cursor.fetchone()
            #     return 
            print(return_result)
            return return_result

async def set_reaction(user_id, direct_id, reaction):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        query = ("UPDATE views SET first_reaction = %s WHERE first_id = %s AND direct_id = %s")
        val = (reaction, user_id, direct_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()

async def get_username(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:   
        await cursor.execute(f"SELECT username FROM users WHERE user_id = '{user_id}'")
        username = (await cursor.fetchone())['username']
        return username
    
async def set_direct_reaction(user_id, direct_id, reaction):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        query = ("UPDATE views SET direct_reaction = %s WHERE first_id = %s AND direct_id = %s")
        val = (reaction, user_id, direct_id) 
        try:
            await cursor.execute(query,val) 
            await conn.commit() 
        except Exception as ex: 
            print('Ошибка ',ex)
            await conn.rollback()         
        return await cursor.fetchall()
    
async def get_anket_where_not_ckeck(user_id):
    conn = await aiomysql.connect(user=config.user, password=config.password, host=config.host, db=config.db)
    async with conn.cursor(aiomysql.DictCursor) as cursor:   
        await cursor.execute(f"SELECT first_id FROM views WHERE direct_id = '{user_id}' AND direct_reaction = 0")
        ankets_list = await cursor.fetchall()
        return ankets_list
    


