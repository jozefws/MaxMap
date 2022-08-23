import mysql.connector
import constants as cn


def create_conn():
    try:
        norris_db = mysql.connector.connect(
        host="localhost",
        user= cn.NORRIS_USERNAME,
        password=cn.NORRIS_SQL_ACCESS,
        database= cn.DATABASE_NAME)
        cursor = norris_db.cursor(buffered=True)
        return norris_db, cursor
    except Exception as e:
        return False, "Exception occured, " + str(e)


def already_added(lat, lng):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        sql = "SELECT * FROM mapbox WHERE lat = %s AND lng = %s"
        cursor.execute(sql, (lat, lng))
        norris_db.commit()
        if(cursor.rowcount > 0):
            return True, cursor.fetchone()[0]
        else:
            return False, "Not added"


def user_already_added(user_id):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        sql = "SELECT * FROM maxmap WHERE discordid = %s"
        cursor.execute(sql, [user_id])
        norris_db.commit()
        if(cursor.rowcount > 0):
            return True, "Already added"
        else:
            return False, "'The user has not added a city'"

    
def add_city_to_mapboxdb(city, country, lat, lng, mapboxref):
    if(not city or not country or not lat or not lng or not mapboxref):
        return False, "Could not add city to mapbox database, missing parameters"
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        count = 1
        try:
            sql = "INSERT INTO mapbox (city, country, lat, lng, mapboxref, count) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (city, country, lat, lng, mapboxref, count))
            norris_db.commit()
            if(cursor.rowcount > 0):
                return True, cursor.lastrowid
            else:
                return False, "Could not add " + city +"'s city to the mapbox database"
        except Exception as e:
            return False, "Exception occured, " + str(e)


def add_city_to_maxmapdb(user_id, discordusdi, mapboxID):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        try:
            sql = "INSERT INTO maxmap (discordid, discordusdi, mapboxID) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, discordusdi, mapboxID))
            norris_db.commit()
            if(cursor.rowcount > 0):
                return True, "Added " +discordusdi +"'s city to the maxmap database"
            else:
                return False, "Could not add " +discordusdi +"'s city to the maxmap database"
        except Exception as e:
            return False, "Exception occured, " + str(e)


def increment_city(lat, lng):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        try:
            sql = "UPDATE mapbox SET count = count + 1 WHERE lat = %s AND lng = %s"
            cursor.execute(sql, (lat, lng))
            norris_db.commit()
            if(cursor.rowcount > 0):
                return True, cursor.lastrowid
            else:
                return False, "Could not increment count"
        except Exception as e:
            return False, "Exception occured, " + str(e)


def get_feature_id(mapboxid):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        try:
            sql = "SELECT mapboxref FROM mapbox WHERE idmapbox = %s"
            cursor.execute(sql, [mapboxid])
            norris_db.commit()
            if(cursor.rowcount > 0):
                return True, cursor.fetchone()[0]
            else:
                return False, "Could not find feature id"
        except Exception as e:
            return False, "Exception occured, " + str(e)

def get_names_and_count(featureID):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database", ""
    else:
        try:
            sql = "SELECT idmapbox, count FROM mapbox WHERE mapboxref = %s"
            cursor.execute(sql, [featureID])
            norris_db.commit()
            if(cursor.rowcount > 0):
                result = cursor.fetchone()
              
                mbid = result[0]
                count = result[1]
            else:
                return False, "Could not find feature id", ""
        except Exception as e:
            return False, "Exception occured, " + str(e), ""
        try:
            sql = "SELECT discordusdi FROM maxmap WHERE mapboxID = %s"
            cursor.execute(sql, [mbid])
            norris_db.commit()
            if(cursor.rowcount > 0):
                discordusdi = cursor.fetchall()
                names = ""
                for name in discordusdi:
                    names = names + "," + name[0]
                return True, count, names
            else:
                return False, "Could not find any users to that city.", ""
        except Exception as e:
            return False, "Exception occured, " + str(e), ""

def delete_city_from_maxmapdb(userID):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database"
    else:
        try:
            sql = "SELECT mapboxID FROM maxmap WHERE discordid = %s"
            cursor.execute(sql, [userID])
            norris_db.commit()
            if(cursor.rowcount > 0):
                mapboxID = cursor.fetchone()[0]
            else:
                return False, "Could not find mapboxID"

            sql = "DELETE FROM maxmap WHERE discordid = %s"
            cursor.execute(sql, [userID])
            norris_db.commit()
            if(cursor.rowcount > 0):
                return True, mapboxID 
            else:
                return False, "Could not delete " +userID +" city from the maxmap database"
        except Exception as e:
            return False, "Exception occured, " + str(e)

def decrement_city(mapboxID):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database", False
    else:
        try:
            sql = "SELECT mapboxref, count FROM mapbox WHERE idmapbox = %s"
            cursor.execute(sql, [mapboxID])
            norris_db.commit()
            if(cursor.rowcount > 0):
                result = cursor.fetchone()
                mapboxref = result[0]
                count = result[1]
            else:
                print("DEC CIT - " + str(mapboxID))
                return False, "Could not find mapboxref", False

            if(count == 1):
                sql = "DELETE FROM mapbox WHERE idmapbox = %s"
                cursor.execute(sql, [mapboxID])
                norris_db.commit()
                if(cursor.rowcount > 0):
                    return True, mapboxref, True
                else:
                    return False, "Could not delete city from mapbox database", False
            else:
                sql = "UPDATE mapbox SET count = count - 1 WHERE idmapbox = %s"
                cursor.execute(sql, [mapboxID])
                norris_db.commit()
                if(cursor.rowcount > 0):
                    return True, mapboxref, False
                else:
                    return False, "Could not decrement count", False
        except Exception as e:
            return False, "Exception occured, " + str(e), False

def get_lat_lng(featureID):
    norris_db, cursor = create_conn()
    if(norris_db == False):
        return False, "Could not connect to the database", False
    else:
        try:
            sql = "SELECT lat, lng FROM mapbox WHERE mapboxref = %s"
            cursor.execute(sql, [featureID])
            norris_db.commit()
            if(cursor.rowcount > 0):
                result = cursor.fetchone()
                lat = result[0]
                lng = result[1]
                return True, lat, lng
            else:
                return False, "Could not find lat and lng", False
        except Exception as e:
            return False, "Exception occured, " + str(e), False