import discord
from discord import app_commands
from discord.ext import commands
import random  
import time
import datetime
import calendar
import sqlite3

ts = calendar.timegm(time.gmtime())
intent = discord.Intents().all()
intent.message_content = True
intent.members = True
intent.guilds = True
bot = commands.Bot(command_prefix='$', intents=intent)
client = discord.Client(intents=intent)
tree = app_commands.CommandTree(client)
liste_embed = ['JSK dev', 'JS', 'JSK']

class SwitchWeaponView(discord.ui.View):
    def __init__(self, weapons, user_id):
        super().__init__()
        self.add_item(WeaponSelect(weapons, user_id))
class WeaponSelect(discord.ui.Select):
    def __init__(self, weapons, user_id):
        # On ne garde que les armes valides
        valid_weapons = [weapon for weapon in weapons if weapon and weapon.lower() != 'none']

        options = [discord.SelectOption(label=weapon, value=weapon) for weapon in valid_weapons]
        super().__init__(placeholder="Choisissez une arme...", options=options)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        selected_weapon = self.values[0]
        
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Déséquipe l'ancienne arme
        cursor.execute('''
        UPDATE user_inventory
        SET equipped = 0
        WHERE utilisateur_id = ? AND equipped = 1
        ''', (self.user_id,))
        
        # Équipe la nouvelle arme
        cursor.execute('''
        UPDATE user_inventory
        SET equipped = 1
        WHERE utilisateur_id = ? AND armes_nom = ?
        ''', (self.user_id, selected_weapon))
        
        conn.commit()
        conn.close()
        
        await interaction.response.send_message(f"L'arme {selected_weapon} est maintenant équipée par {interaction.user.name}!", ephemeral=False)

def get_equipped_weapon(utilisateurs_id):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT armes_nom
    FROM user_inventory
    WHERE utilisateurs_id = ? AND equipped = 1
    ''', (utilisateurs_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return "Aucune arme équipée"
def equip_weapon(utilisateurs_id, weapon_name):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Déséquiper l'ancienne arme (si elle est déjà équipée)
    cursor.execute('''
    UPDATE user_inventory
    SET equipped = 0
    WHERE utilisateurs_id = ? AND equipped = 1
    ''', (utilisateurs_id,))
    
    # Équiper la nouvelle arme
    cursor.execute('''
    INSERT INTO user_inventory (utilisateurs_id, armes_nom, equipped)
    VALUES (?, ?, 1)
    ON CONFLICT(utilisateurs_id, armes_nom)
    DO UPDATE SET equipped = 1
    WHERE utilisateurs_id = ? AND armes_nom = ?
    ''', (utilisateurs_id, weapon_name, utilisateurs_id, weapon_name))
    
    conn.commit()
    conn.close()
def get_user_data(discord_id):
    conn = sqlite3.connect('test.db')  # Nom de ta base de données
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT cc, ct, e, f, name FROM utilisateurs
            WHERE discord_id = ?
        ''', (discord_id,))
        result = cursor.fetchone()
        print(f"Données récupérées pour ID {discord_id}: {result}")  # Message de débogage
        return result
    except sqlite3.Error as e:
        print(f"Erreur lors de l'accès à la base de données : {e}")
        return None
    finally:
        conn.close()  
def update_user_stat(discord_id, column, value):
    conn = sqlite3.connect('test.db', timeout=10)  # Nom de ta base de données
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'''
            UPDATE utilisateurs
            SET {column} = ?
            WHERE discord_id = ?
        ''', (value, discord_id))
        conn.commit()
        
        # Vérifier si des lignes ont été modifiées
        if cursor.rowcount == 0:
            return "Aucun utilisateur trouvé avec cet ID."
        
        return "Mise à jour réussie."
    except sqlite3.Error as e:
        return f"Une erreur est survenue lors de la mise à jour : {e}"
    finally:
        conn.close()   
def get_simple_id(discord_id):
    conn = sqlite3.connect('test.db', timeout=10)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT simple_id FROM utilisateurs_mapping
            WHERE discord_id = ?
        ''', (discord_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        return None
    finally:
        conn.close()
def is_owner():
    def predicate(interaction: discord.Interaction):
        if interaction.user.id == interaction.guild.owner.id:
            return True
    return app_commands.check(predicate)
def lancerUnDe(n):
    d = random.randint(1, n)
    return d
def lancerDeDes(nbDes, nbFaces, ajout):
    total = 0
    for _ in range(nbDes):
        total += random.randint(1, nbFaces)
    return total + ajout
def sommeDeDes(nbDes,nbFaces):
    S = 0    #somme des dés, pour l'instant nulle
    for i in range(nbDes):
        d = lancerUnDe(nbFaces) #on lance un dé
        S=S+d     #on ajoute ce dé à la somme
    return S

        
# @bot.event    
# Toutes les commandes:   
    
#Commande pour MJ 
@bot.tree.command(guild=discord.Object(id=0), name="ajouter_mapping", description="Ajoute une entrée dans la table utilisateurs_mapping")
@commands.has_role("Maître du jeu")  # Assure que seul les Maître du jeu peuvent exécuter cette commande
async def ajouter_mapping(interaction: discord.Interaction, discord_id: int, simple_id: int, name: str):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'entrée existe déjà
        cursor.execute('SELECT 1 FROM utilisateurs_mapping WHERE discord_id = ?', (discord_id,))
        if cursor.fetchone():
            await interaction.response.send_message(f"Une entrée avec le discord_id {discord_id} existe déjà.", ephemeral=True)
            return

        # Ajouter l'entrée dans la table utilisateurs_mapping
        cursor.execute('''
            INSERT INTO utilisateurs_mapping (discord_id, simple_id, Name) 
            VALUES (?, ?, ?)
        ''', (discord_id, simple_id, name))
        
        conn.commit()
        await interaction.response.send_message(f"Entrée ajoutée avec succès : Discord ID {discord_id}, Simple ID {simple_id}, Name {name}.")
    
    except Exception as e:
        await interaction.response.send_message(f"Une erreur est survenue : {e}", ephemeral=True)
    
    finally:
        conn.close()
        
@bot.tree.command(guild=discord.Object(id=0), name="ajouter_utilisateur", description="Ajouter un nouvel utilisateur avec toutes les colonnes renseignées.")
@app_commands.checks.has_role("Maître du jeu")
async def ajouter_utilisateur(interaction: discord.Interaction, 
                              name: str, 
                              simple_id: int, 
                              arme: str, 
                              cc: int, 
                              ct: int, 
                              endurance: int,  # 'e' devient 'endurance'
                              force: int,      # 'f' devient 'force'
                              b: int,         # 'b' devient 'pv'
                              initiative: int,  # 'I' devient 'intelligence'
                              attaque_par_round: int,    # 'A' devient 'agilité'
                              dextérité: int,  # 'Dex' devient 'dextérité'
                              commandement: int,   # 'Cd' devient 'charisme'
                              intelligence: int,  # 'Int' devient 'intelligence_nat'
                              calme: int, # 'Cl' devient 'sang_froid'
                              force_mentale: int,  # 'FM' devient 'force_mentale'
                              sociabilité: int,     # 'Soc' devient 'social'
                              pointdestin: int, 
                              pointfolie: int, 
                              xpautilise: int, 
                              inventory_id: int):
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Insertion des données dans la table utilisateurs
        cursor.execute('''
            INSERT INTO utilisateurs (Name, discord_id, arme, cc, ct, e, f, b, I, A, Dex, Cd, Int, Cl, FM, Soc, Pointdestin, Pointfolie, XPautilise, Inventory_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, simple_id, arme, cc, ct, endurance, force, b, initiative, attaque_par_round, dextérité, commandement, intelligence, calme, force_mentale, sociabilité, pointdestin, pointfolie, xpautilise, inventory_id))
        
        conn.commit()
        
        await interaction.response.send_message(f"Utilisateur '{name}' ajouté avec succès.", ephemeral=True)
    except sqlite3.Error as e:
        await interaction.response.send_message(f"Erreur lors de l'ajout de l'utilisateur : {e}", ephemeral=True)
    finally:
        conn.close()

@ajouter_utilisateur.error
async def ajouter_utilisateur_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("Désolé, vous n'avez pas les permissions nécessaires pour exécuter cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Une erreur s'est produite : {error}", ephemeral=True)       
@bot.tree.command(guild=discord.Object(id=0), name="degat", description="Modifie directement les points de vie (statistique B) d'un utilisateur.")
@app_commands.checks.has_role("Maître du jeu")
async def degat(interaction: discord.Interaction, cible_id: int, montant: str):
    conn = sqlite3.connect('test.db', timeout=10)
    cursor = conn.cursor()

    try:
        # Récupérer la statistique "B" actuelle
        cursor.execute('''
            SELECT B FROM utilisateurs WHERE discord_id = ?
        ''', (cible_id,))
        result = cursor.fetchone()
        
        if not result:
            await interaction.response.send_message(f"Aucune donnée trouvée pour l'utilisateur avec l'ID Discord {cible_id}.", ephemeral=True)
            return
        
        valeur_B_actuelle = result[0]

        # Vérifier si le montant est positif ou négatif
        if montant.startswith('+'):
            modification = int(montant[1:])  # Exclut le signe + et convertit en entier
        elif montant.startswith('-'):
            modification = -int(montant[1:])  # Exclut le signe - et convertit en entier
        else:
            modification = int(montant)  # Si aucun signe, considère que c'est un ajout

        # Calculer la nouvelle valeur de B
        nouvelle_valeur_B = valeur_B_actuelle + modification
        
        # Empêcher les points de vie d'aller en dessous de 0
        if nouvelle_valeur_B < 0:
            nouvelle_valeur_B = 0
        
        # Mettre à jour la statistique B dans la base de données
        cursor.execute('''
            UPDATE utilisateurs
            SET B = ?
            WHERE discord_id = ?
        ''', (nouvelle_valeur_B, cible_id))
        conn.commit()

        # Réponse indiquant la modification
        if modification >= 0:
            action = "gagné"
        else:
            action = "perdu"

        await interaction.response.send_message(
            f"L'utilisateur avec l'ID Discord {cible_id} a {action} {abs(modification)} points de vie.\n"
            f"Nouvelle valeur de B : {nouvelle_valeur_B}.",
            ephemeral=False
        )

    except Exception as e:
        await interaction.response.send_message(f"Une erreur s'est produite : {str(e)}", ephemeral=True)
    finally:
        conn.close()
        
@bot.tree.command(guild=discord.Object(id=0), name="clear", description="Supprimer des messages")
@is_owner()
async def clear(interaction: discord.Interaction, amount: int, channel: discord.TextChannel= None):
    
    if channel is None:
        channel = interaction.channel

    channel1 = interaction.guild.get_channel(1195188230107172975)
    
    embed = discord.Embed(title="Clear", description="Un modérateur a supprimé des messages!", color=discord.Color.green())
    embed.add_field(name="Informations Modérateur", value=f"-> 'Utilisateur': {interaction.user.mention}\n> 'Nom': {interaction.user.name}#{interaction.user.discriminator}", inline=False)
    embed.add_field(name="Informations Message", value=f"-> 'Date': <t:{ts}:R>\n-> 'salon' : {channel.mention}\n> 'Nombre de messages':\n''' {amount}'''", inline=False)
    embed.set_footer(text=random.choice(liste_embed))
    embed.timestamp = datetime.datetime.now()
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await channel1.send(embed=embed)
    await channel.purge(limit=amount)
    
@bot.tree.command(guild=discord.Object(id=0), name="update", description="Met à jour une statistique d'un utilisateur ou l'argent dans l'inventaire.")
@app_commands.checks.has_role("Maître du jeu")
async def update(interaction: discord.Interaction, user_id: int, stat: str, new_value: int, id: int = None):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    if stat == 'argent':
        if id is None:
            await interaction.response.send_message("Veuillez spécifier l'ID de l'entrée à mettre à jour.", ephemeral=True)
            conn.close()
            return
        
        # Mettre à jour une entrée spécifique dans la table "user_inventory"
        cursor.execute('''
            UPDATE user_inventory
            SET argent = ?
            WHERE utilisateur_id = ? AND id = ?
        ''', (new_value, user_id, id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            await interaction.response.send_message(f"Argent mis à jour à {new_value} pour l'entrée ID {id} de l'utilisateur avec ID {user_id}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Aucune entrée trouvée avec l'ID {id} pour l'utilisateur avec ID {user_id}.", ephemeral=True)

    elif stat in ['cc', 'ct', 'e', 'f', 'b', 'I', 'A', 'Dex', 'Cd', 'Int', 'Cl', 'FM', 'Soc']:
        result = update_user_stat(user_id, stat, new_value)
        await interaction.response.send_message(result, ephemeral=True)
    
    else:
        await interaction.response.send_message("Statistique invalide. Utilisez `cc`, `ct`, `e`, `f`, `b`, `I`, `A`, `Dex`, `Cd`, `Int`, `Cl`, `FM`, `Soc` ou `argent`.", ephemeral=True)
    
    conn.close()
def update_user_stat(user_id, stat, new_value):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute(f'''
        UPDATE utilisateurs
        SET {stat} = ?
        WHERE simple_id = ?
    ''', (new_value, user_id))
    
    conn.commit()
    
    if cursor.rowcount > 0:
        message = f"Statistique {stat} mise à jour à {new_value} pour l'utilisateur avec ID {user_id}."
    else:
        message = f"Aucun utilisateur trouvé avec l'ID {user_id}."

    conn.close()
    return message

@bot.tree.command(guild=discord.Object(id=0), name="aie", description="Gère les dégâts lors d'une attaque")
@app_commands.checks.has_role("Maître du jeu")
async def aie(interaction: discord.Interaction, cible_id: int, attaquant_id: int):
    conn = sqlite3.connect('test.db', timeout=10)
    cursor = conn.cursor()
    
    # Vérifier si un résultat de D100CC est stocké pour cette attaque
    if (attaquant_id, cible_id) not in recent_rolls:
        await interaction.response.send_message("Aucun jet de D100CC trouvé pour cette attaque.", ephemeral=True)
        return
    
    resultat_d100 = recent_rolls.pop((attaquant_id, cible_id))  # Récupère et supprime le résultat du D100
    resultat_inversé = int(str(resultat_d100)[::-1])  # Inverser le résultat du D100
    
    # Déterminer la localisation de l'attaque
    if 1 <= resultat_inversé <= 15:
        location = "Tête"
    elif 16 <= resultat_inversé <= 35:
        location = "Bras droit"
    elif 36 <= resultat_inversé <= 55:
        location = "Bras gauche"
    elif 56 <= resultat_inversé <= 80:
        location = "Torse"
    elif 81 <= resultat_inversé <= 90:
        location = "Jambe droite"
    else:  # 91-100
        location = "Jambe gauche"

    # Obtenir les statistiques de la cible
    cursor.execute('''
        SELECT cc, ct, e, f, B FROM utilisateurs WHERE discord_id = ?
    ''', (cible_id,))
    stats_cible = cursor.fetchone()
    
    cursor.execute('''
        SELECT Name FROM utilisateurs_mapping WHERE simple_id = ?
    ''', (cible_id,))
    cible_name = cursor.fetchone()
    
    if cible_name:
        cible_name = cible_name[0]
    else:
        cible_name = "Inconnu"
    
    # Obtenir le nom et les statistiques de l'attaquant
    cursor.execute('''
        SELECT Name FROM utilisateurs_mapping WHERE simple_id = ?
    ''', (attaquant_id,))
    attaquant_name = cursor.fetchone()
    
    if attaquant_name:
        attaquant_name = attaquant_name[0]
    else:
        attaquant_name = "Inconnu"
    
    # Obtenir l'arme équipée de l'attaquant
    cursor.execute('''
        SELECT armes_nom FROM user_inventory WHERE utilisateur_id = ? AND equipped = 1
    ''', (attaquant_id,))
    arme_result = cursor.fetchone()
    
    if not arme_result:
        await interaction.response.send_message(f"{attaquant_name} n'a pas d'arme équipée.", ephemeral=True)
        conn.close()
        return
    
    arme_attaquant = arme_result[0]

    # Obtenir les statistiques et les détails de l'arme de l'attaquant
    cursor.execute('''
        SELECT cc, ct, e, f FROM utilisateurs WHERE discord_id = ?
    ''', (attaquant_id,))
    stats_attaquant = cursor.fetchone()
    
    if not stats_attaquant:
        await interaction.response.send_message("Données non trouvées pour l'utilisateur spécifié.", ephemeral=True)
        conn.close()
        return

    cursor.execute('''
        SELECT type, degats FROM armes WHERE nom = ?
    ''', (arme_attaquant,))
    arme_details = cursor.fetchone()
    
    if not arme_details:
        await interaction.response.send_message(f"Aucune information trouvée pour l'arme '{arme_attaquant}'.", ephemeral=True)
        conn.close()
        return
    
    type_arme, degats_arme = arme_details
    
    # Vérifier l'armure de la cible pour la localisation de l'attaque
    cursor.execute('''
        SELECT ui.armures_nom, a.protection
        FROM user_inventory ui
        JOIN armures a ON ui.armures_nom = a.nom
        WHERE ui.utilisateur_id = ? AND a.Location = ?
    ''', (cible_id, location))
    
    armure_result = cursor.fetchone()
    protection_armure = 0
    
    if armure_result:
        protection_armure = armure_result[1]
    
    # Calculer les dégâts totaux
    resultat_de = lancerDeDes(1, 6, 0)

    if type_arme in ['arme dist simple', 'arme dist avancée']:
        degats_totaux = degats_arme + resultat_de - stats_cible[2] - protection_armure  # - e de la cible et protection de l'armure
        
        # Créer la réponse pour les armes à distance
        reponse = (
            f"**Dégâts infligés par l'attaque:**\n"
            f"- L'arme de {attaquant_name} est : {arme_attaquant}, qui est une {type_arme}.\n"
            f"- Dégâts de l'arme: {degats_arme}\n"
            f"- Le D6 donne : {resultat_de}\n"
            f"- L'endurance de {cible_name} est de {stats_cible[2]}.\n"
            f"- La protection de l'armure ({location}) est de {protection_armure}.\n"
            f"- Calcul final : {degats_arme} + {resultat_de} - {stats_cible[2]} - {protection_armure} = {degats_totaux}\n"
            f"- Dégâts totaux infligés : {degats_totaux} sur {cible_name}.\n"
        )
    else:
        degats_totaux = stats_attaquant[3] + resultat_de + degats_arme - stats_cible[2] - protection_armure  # f de l'attaquant + dégâts de l'arme - e de la cible - protection de l'armure

        # Créer la réponse pour les armes de mêlée
        reponse = (
            f"**Dégâts infligés par l'attaque:**\n"
            f"- L'arme de {attaquant_name} est : {arme_attaquant}, qui est une {type_arme}.\n"
            f"- Dégâts de l'arme: {degats_arme}\n"
            f"- Force de l'attaquant : {stats_attaquant[3]}\n"
            f"- Le D6 donne : {resultat_de}\n"
            f"- L'endurance de {cible_name} est de {stats_cible[2]}.\n"
            f"- La protection de l'armure ({location}) est de {protection_armure}.\n"
            f"- Calcul final : {degats_arme} + {resultat_de} + {stats_attaquant[3]} - {stats_cible[2]} - {protection_armure} = {degats_totaux}\n"
            f"- Dégâts totaux infligés : {degats_totaux} sur {cible_name}.\n"
        )
    
    # Mettre à jour la statistique "B" de la cible en soustrayant les dégâts totaux
    nouvelle_valeur_B = stats_cible[4] - degats_totaux
  
    
    cursor.execute('''
        UPDATE utilisateurs
        SET B = ?
        WHERE discord_id = ?
    ''', (nouvelle_valeur_B, cible_id))
    conn.commit()
    
    # Ajouter l'information sur la mise à jour des points de vie dans la réponse
    reponse += (
        f"\n{cible_name} a maintenant {nouvelle_valeur_B} points de vie (statistique B) restants."
    )
    
    await interaction.response.send_message(reponse, ephemeral=False)
    conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_inventaire", description="Ajoute un objet dans l'inventaire d'un utilisateur.")
@commands.has_role("Maître du jeu")
async def ajouter_inventaire(interaction: discord.Interaction, utilisateur_id: int, armes_nom: str, armures_nom: str, divers_nom: str, equipped: int, argent: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Convertir "null" en valeur NULL pour la base de données
    if armes_nom.lower() == "null":
        armes_nom = None
    if armures_nom.lower() == "null":
        armures_nom = None
    if divers_nom.lower() == "null":
        divers_nom = None

    try:
        cursor.execute('''
            INSERT INTO user_inventory (utilisateur_id, armes_nom, armures_nom, divers_nom, equipped, argent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (utilisateur_id, armes_nom, armures_nom, divers_nom, equipped, argent))
        
        conn.commit()
        await interaction.response.send_message(f"L'inventaire de l'utilisateur {utilisateur_id} a été mis à jour avec succès.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_armes", description="Affiche la liste complète des armes.")
@commands.has_role("Maître du jeu")
async def afficher_armes(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT nom FROM armes')
        armes = cursor.fetchall()

        if armes:
            armes_list = "\n".join([f"- {arme[0]}" for arme in armes])
            await interaction.response.send_message(f"**Liste des armes disponibles :**\n{armes_list}", ephemeral=True)
        else:
            await interaction.response.send_message("Aucune arme trouvée.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_armures", description="Affiche la liste complète des armures.")
@commands.has_role("Maître du jeu")
async def afficher_armures(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT nom FROM armures')
        armures = cursor.fetchall()

        if armures:
            armures_list = "\n".join([f"- {armure[0]}" for armure in armures])
            await interaction.response.send_message(f"**Liste des armures disponibles :**\n{armures_list}", ephemeral=True)
        else:
            await interaction.response.send_message("Aucune armure trouvée.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_divers", description="Affiche la liste complète des objets divers.")
@commands.has_role("Maître du jeu")
async def afficher_divers(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT nom FROM divers')
        divers = cursor.fetchall()

        if divers:
            divers_list = "\n".join([f"- {diver[0]}" for diver in divers])
            await interaction.response.send_message(f"**Liste des objets divers disponibles :**\n{divers_list}", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun objet divers trouvé.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_divers", description="Ajoute un nouvel objet dans la table Divers.")
@commands.has_role("Maître du jeu")
async def ajouter_divers(interaction: discord.Interaction, nom: str, prix: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO divers (nom, prix) VALUES (?, ?)', (nom, prix))
        conn.commit()
        await interaction.response.send_message(f"L'objet divers '{nom}' a été ajouté avec succès.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_arme", description="Ajoute une nouvelle arme dans la table Armes.")
@commands.has_role("Maître du jeu")
async def ajouter_arme(interaction: discord.Interaction, nom: str, type: str, degats: int, prix: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO armes (nom, type, degats, prix) VALUES (?, ?, ?, ?)', (nom, type, degats, prix))
        conn.commit()
        await interaction.response.send_message(f"L'arme '{nom}' a été ajoutée avec succès.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_armure", description="Ajoute une nouvelle armure dans la table Armures.")
@commands.has_role("Maître du jeu")
async def ajouter_armure(interaction: discord.Interaction, nom: str, type: str, protection: int, prix: int, location: str):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO armures (nom, type, protection, prix, location) VALUES (?, ?, ?, ?, ?)', (nom, type, protection, prix, location))
        conn.commit()
        await interaction.response.send_message(f"L'armure '{nom}' a été ajoutée avec succès.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="helpmj", description="Affiche la liste des commandes disponibles pour les Maîtres du jeu.")
@commands.has_role("Maître du jeu")
async def help_mj(interaction: discord.Interaction):
    embed = discord.Embed(title="Liste des commandes pour les Maîtres du jeu", color=discord.Color.blue())
    embed.add_field(name="Liste des commandes pour afficher des informations :", value="/afficher_liste_sort, /afficher_liste_competence, /afficher_liste_utilisateur, /afficher_liste_divers, /afficher_liste_armes, /afficher_liste_armures", inline=False)
    embed.add_field(name="Liste des commandes pour ajouter des informations dans la base de donnée", value="/ajouter_sort, /ajouter_sort_utilisateur, /ajouter_competence, /ajouter_competence_utilisateur, /ajouter_mapping, /ajouter_utilisateur, /ajouter_divers, /ajouter_arme, /ajouter_armure, /ajouter_inventaire", inline=False)
    embed.add_field(name="Autres commandes", value="/degat, /update, /aie", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_sort", description="Ajoute un nouveau sort dans la table des sorts.")
@commands.has_role("Maître du jeu")
async def ajouter_sort(interaction: discord.Interaction, nom: str, pm: int, composant: str, description: str, duree: str, portee: str, temps_incantation: str):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Convertir "null" en valeur NULL pour la base de données
    if composant.lower() == "null":
        composant = None
    if description.lower() == "null":
        description = None
    if duree.lower() == "null":
        duree = None
    if portee.lower() == "null":
        portee = None
    if temps_incantation.lower() == "null":
        temps_incantation = None

    try:
        cursor.execute('''
            INSERT INTO Sorts (Nom, PM, Composant, Description, Durée, Portée, "Temps d'incantation")
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nom, pm, composant, description, duree, portee, temps_incantation))
        
        conn.commit()
        await interaction.response.send_message(f"Le sort '{nom}' a été ajouté avec succès à la table des sorts.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_sort_utilisateur", description="Assigne un sort existant à un utilisateur.")
@commands.has_role("Maître du jeu")
async def ajouter_sort_utilisateur(interaction: discord.Interaction, utilisateur_id: int, sort_id: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Vérifier si l'utilisateur et le sort existent
        cursor.execute('SELECT 1 FROM utilisateurs WHERE discord_id = ?', (utilisateur_id,))
        utilisateur_existe = cursor.fetchone()
        
        cursor.execute('SELECT 1 FROM Sorts WHERE id = ?', (sort_id,))
        sort_existe = cursor.fetchone()

        if not utilisateur_existe:
            await interaction.response.send_message(f"L'utilisateur avec ID {utilisateur_id} n'existe pas.", ephemeral=True)
            return

        if not sort_existe:
            await interaction.response.send_message(f"Le sort avec ID {sort_id} n'existe pas.", ephemeral=True)
            return

        # Ajouter le sort à l'utilisateur
        cursor.execute('''
            INSERT INTO utilisateurs_sorts (utilisateur_id, sort_id)
            VALUES (?, ?)
        ''', (utilisateur_id, sort_id))

        conn.commit()
        await interaction.response.send_message(f"Le sort ID {sort_id} a été assigné à l'utilisateur ID {utilisateur_id} avec succès.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_sorts", description="Affiche la liste des sorts avec leur ID.")
@commands.has_role("Maître du jeu")
async def liste_sorts(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer la liste des sorts
        cursor.execute('SELECT id, Nom FROM Sorts')
        sorts = cursor.fetchall()

        if sorts:
            # Formatage des résultats pour un affichage propre
            liste_sorts = "\n".join([f"ID: {sort[0]} - Nom: {sort[1]}" for sort in sorts])
            message = f"Liste des sorts disponibles:\n{liste_sorts}"
        else:
            message = "Aucun sort trouvé dans la base de données."

        await interaction.response.send_message(message, ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_utilisateurs", description="Affiche la liste des utilisateurs avec leur simple_id.")
@commands.has_role("Maître du jeu")
async def liste_utilisateurs(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer la liste des utilisateurs
        cursor.execute('SELECT simple_id, Name FROM utilisateurs_mapping')
        utilisateurs = cursor.fetchall()

        if utilisateurs:
            # Formatage des résultats pour un affichage propre
            liste_utilisateurs = "\n".join([f"Simple ID: {utilisateur[0]} - Nom: {utilisateur[1]}" for utilisateur in utilisateurs])
            message = f"Liste des utilisateurs:\n{liste_utilisateurs}"
        else:
            message = "Aucun utilisateur trouvé dans la base de données."

        await interaction.response.send_message(message, ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_competence", description="Ajoute une nouvelle compétence à la table 'competences'.")
@commands.has_role("Maître du jeu")
async def ajouter_competence(interaction: discord.Interaction, nom: str):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Insertion de la nouvelle compétence dans la table 'competences'
        cursor.execute('INSERT INTO competences (nom) VALUES (?)', (nom,))
        conn.commit()

        await interaction.response.send_message(f"La compétence '{nom}' a été ajoutée avec succès.", ephemeral=True)
    except sqlite3.Error as e:
        await interaction.response.send_message(f"Une erreur est survenue lors de l'ajout de la compétence : {e}", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="ajouter_competence_utilisateur", description="Ajoute une compétence existante à un utilisateur")
@commands.has_role("Maître du jeu")
async def ajouter_competence_utilisateur(interaction: discord.Interaction, utilisateur_id: int, competence_id: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Insérer l'entrée dans la table utilisateurs_competences
        cursor.execute('''
            INSERT INTO utilisateurs_competences (utilisateur_id, competence_id)
            VALUES (?, ?)
        ''', (utilisateur_id, competence_id))

        conn.commit()
        await interaction.response.send_message(f"Compétence ID {competence_id} ajoutée avec succès à l'utilisateur ID {utilisateur_id}.")
    
    except sqlite3.Error as e:
        await interaction.response.send_message(f"Erreur lors de l'ajout de la compétence : {str(e)}", ephemeral=True)
    
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="afficher_liste_competences", description="Affiche la liste de toutes les compétences.")
@commands.has_role("Maître du jeu")
async def liste_competences(interaction: discord.Interaction):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer toutes les compétences de la table 'competences'
        cursor.execute('SELECT id, nom FROM competences')
        competences = cursor.fetchall()

        if competences:
            # Créer une liste de compétences pour l'affichage
            liste_competences = "\n".join([f"{comp[0]}: {comp[1]}" for comp in competences])
            await interaction.response.send_message(f"**Liste des compétences :**\n{liste_competences}", ephemeral=True)
        else:
            await interaction.response.send_message("Aucune compétence trouvée dans la base de données.", ephemeral=True)
    except sqlite3.Error as e:
        await interaction.response.send_message(f"Une erreur est survenue lors de la récupération des compétences : {e}", ephemeral=True)
    finally:
        conn.close()



#Commande pour les joueurs
@bot.tree.command(guild=discord.Object(id=0), name="plandecarriere", description="Affiche le plan de carrière d'un utilisateur.")
async def afficher_plan_carriere(interaction: discord.Interaction, discord_id: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Message de débogage
        print(f"Tentative de récupération du plan de carrière pour ID {discord_id}")

        # Requête pour obtenir les informations du plan de carrière
        cursor.execute('''
            SELECT * FROM plan_carriere WHERE discord_id = ?
        ''', (discord_id,))
        
        result = cursor.fetchone()

        if result:
            # Décomposer les résultats
            (
                discord_id, cc, ct, e, f, b, I, A, Dex, Cd, Int, Cl, FM, Soc
            ) = result
            
            # Formater les données pour l'affichage
            reponse = (
                f"**Plan de Carrière pour ID {discord_id} :**\n"
                f"- CC: {cc}\n"
                f"- CT: {ct}\n"
                f"- E: {e}\n"
                f"- F: {f}\n"
                f"- B: {b}\n"
                f"- I: {I}\n"
                f"- A: {A}\n"
                f"- Dex: {Dex}\n"
                f"- Cd: {Cd}\n"
                f"- Int: {Int}\n"
                f"- Cl: {Cl}\n"
                f"- FM: {FM}\n"
                f"- Soc: {Soc}\n"
            )
        else:
            reponse = f"Aucun plan de carrière trouvé pour l'utilisateur avec ID {discord_id}."

        await interaction.response.send_message(reponse, ephemeral=False)
        
    except sqlite3.Error as e:
        print(f"Erreur SQL : {e}")  # Message de débogage
        await interaction.response.send_message(f"Erreur lors de la récupération des données : {e}", ephemeral=True)

    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="comp", description="Affiche la liste des compétences d'un utilisateur spécifique.")
async def afficher_competences(interaction: discord.Interaction, simple_id: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Vérifier si l'utilisateur existe dans la table utilisateurs_mapping
        cursor.execute('SELECT Name FROM utilisateurs_mapping WHERE simple_id = ?', (simple_id,))
        result = cursor.fetchone()

        if not result:
            await interaction.response.send_message(f"Aucun utilisateur trouvé avec le simple ID {simple_id}.", ephemeral=False)
            return

        user_name = result[0]

        # Récupérer la liste des compétences de l'utilisateur
        cursor.execute('''
            SELECT c.nom FROM competences c
            JOIN utilisateurs_competences uc ON c.id = uc.competence_id
            WHERE uc.utilisateur_id = ?
        ''', (simple_id,))

        competences = cursor.fetchall()

        if competences:
            competences_list = "\n".join([f"- {competence[0]}" for competence in competences])
            await interaction.response.send_message(f"Compétences de {user_name} ({simple_id}) :\n{competences_list}", ephemeral=False)
        else:
            await interaction.response.send_message(f"{user_name} ({simple_id}) n'a aucune compétence.", ephemeral=False)

    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="sorts", description="Affiche la liste des sorts d'un utilisateur spécifique.")
async def afficher_sorts(interaction: discord.Interaction, simple_id: int):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Vérifier si l'utilisateur existe dans la table utilisateurs_mapping
        cursor.execute('SELECT Name FROM utilisateurs_mapping WHERE simple_id = ?', (simple_id,))
        result = cursor.fetchone()

        if not result:
            await interaction.response.send_message(f"Aucun utilisateur trouvé avec le simple ID {simple_id}.", ephemeral=False)
            return

        user_name = result[0]

        # Récupérer la liste des sorts de l'utilisateur
        cursor.execute('''
            SELECT s.nom FROM sorts s
            JOIN utilisateurs_sorts us ON s.id = us.sort_id
            WHERE us.utilisateur_id = ?
        ''', (simple_id,))

        sorts = cursor.fetchall()

        if sorts:
            sorts_list = "\n".join([f"- {sort[0]}" for sort in sorts])
            await interaction.response.send_message(f"Sorts de {user_name} ({simple_id}) :\n{sorts_list}", ephemeral=False)
        else:
            await interaction.response.send_message(f"{user_name} ({simple_id}) n'a aucun sort.", ephemeral=False)

    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="mes_sorts", description="Affiche la liste de vos sorts.")
async def mes_sorts(interaction: discord.Interaction):
    user_id = interaction.user.id  # Récupère l'ID Discord de l'utilisateur
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id de l'utilisateur à partir de son discord_id
        cursor.execute('SELECT simple_id FROM utilisateurs_mapping WHERE discord_id = ?', (user_id,))
        result = cursor.fetchone()

        if not result:
            await interaction.response.send_message("Aucune donnée utilisateur trouvée.", ephemeral=True)
            return

        simple_id = result[0]

        # Récupérer la liste des sorts de l'utilisateur
        cursor.execute('''
            SELECT s.nom FROM sorts s
            JOIN utilisateurs_sorts us ON s.id = us.sort_id
            WHERE us.utilisateur_id = ?
        ''', (simple_id,))

        sorts = cursor.fetchall()

        if sorts:
            sorts_list = "\n".join([f"- {sort[0]}" for sort in sorts])
            await interaction.response.send_message(f"Voici la liste de vos sorts :\n{sorts_list}", ephemeral=False)
        else:
            await interaction.response.send_message("Vous n'avez aucun sort.", ephemeral=False)

    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="stats", description="Affiche les statistiques d'un utilisateur")
async def stats(interaction: discord.Interaction, discord_id: int):
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id et les statistiques à partir de l'ID Discord
        cursor.execute('''
            SELECT cc, ct, e, f, b, I, A, Dex, Cd, Int, Cl, FM, Soc, Pointfolie, Pointdestin, XPautilise, u.Name 
            FROM utilisateurs u
            JOIN utilisateurs_mapping um ON um.simple_id = u.discord_id
            WHERE um.simple_id = ?
        ''', (discord_id,))
        
        user_data = cursor.fetchone()
        if user_data:
            cc, ct, e, f, b, I, A, Dex, Cd, Int, Cl, FM, Soc, Pointfolie, Pointdestin, XPautilise, Name = user_data
            
            
            # Créer un embed pour afficher les statistiques
            embed = discord.Embed(title="", description=f"Statistiques pour {Name}", color=discord.Color.blue())
            # Préparer les noms et valeurs des statistiques avec alignement
            stats_names = """\
CC  CT  E  F   B   I   A   Dex  CD  INT  CL  FM  SOC
"""
            stats_values = f"""\
{cc:<3} {ct:<3} {e:<2} {f:<3} {b:<3} {I:<3} {A:<3} {Dex:<4} {Cd:<3} {Int:<4} {Cl:<3} {FM:<3} {Soc:<4}
"""

            # Ajouter les champs à l'embed
            embed.add_field(name="Statistiques", value=f"```\n{stats_names}{stats_values}```", inline=False)

            embed.set_footer(text=random.choice(liste_embed))
            embed.timestamp = datetime.datetime.now()
            
            # Créer un embed pour afficher les statistiques
            embed2 = discord.Embed(title="", description=f"Informations pour {Name}", color=discord.Color.green())
            
            stats_names = """\
Point de Destin  Point de Folie  XP à utilisé
"""
            stats_values = f"""\
{Pointdestin:<15} {Pointfolie:<15} {XPautilise:<15}
"""
            embed2.add_field(name="Statistiques", value=f"```\n{stats_names}{stats_values}```", inline=False)
            embed2.set_footer(text=random.choice(liste_embed))
            embed2.timestamp = datetime.datetime.now()
            
            await interaction.response.send_message(embeds=[embed, embed2], ephemeral=False)
        else:
            await interaction.response.send_message(f"Impossible de récupérer les statistiques pour l'ID Discord {discord_id}.", ephemeral=False)
    finally:
        conn.close()
  
@bot.tree.command(guild=discord.Object(id=0),name="d100ct",description="Lance un dé à 100 faces et compare le résultat à la statistique Ct de l'utilisateur."
)
async def d100ct(interaction: discord.Interaction, discord_id: int):
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id à partir de l'ID Discord
        cursor.execute('''
            SELECT simple_id FROM utilisateurs_mapping
            WHERE simple_id = ?
        ''', (discord_id,))

        result = cursor.fetchone()

        if result:
            simple_id = result[0]

            # Récupérer les statistiques de l'utilisateur avec le simple_id
            cursor.execute('''
                SELECT ct FROM utilisateurs
                WHERE discord_id = ?
            ''', (simple_id,))

            user_data = cursor.fetchone()

            if user_data:
                ct = user_data[0]
                resultat_de = random.randint(1, 100)
                if resultat_de > ct:
                    reponse = f"❌ Tu as lancé un {resultat_de}, ce qui est supérieur à ta statistique Ct de {ct}, c'est donc un échec ! ❌"
                else:
                    reponse = f"✅ Tu as lancé un {resultat_de}, ce qui est inférieur ou égal à ta statistique Ct de {ct}, ce qui veut dire que tu réussis ton jet ! ✅"
            else:
                reponse = f"Aucune donnée trouvée pour l'utilisateur avec l'ID Discord {discord_id}."
        else:
            reponse = f"Aucune correspondance trouvée pour l'utilisateur avec l'ID Discord {discord_id}."
    
    finally:
        conn.close()
    
    await interaction.response.send_message(reponse)

@bot.tree.command(guild=discord.Object(id=0), name="d6", description="Lance un dé à 6 faces")
async def d6(interaction: discord.Interaction):
    
    result = random.randint(1, 6)
    # Envoyer le résultat du lancer de dé
    await interaction.response.send_message(f"🎲 Vous avez lancé un D6 et obtenu : **{result}**", ephemeral=False)

recent_rolls = {}
@bot.tree.command(guild=discord.Object(id=0), name="d100cc", description="Lance un dé à 100 faces et compare le résultat à la statistique CC de l'utilisateur.")
async def d100cc(interaction: discord.Interaction, discord_id: int, cible_id: int):
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id à partir de l'ID Discord
        cursor.execute('''
            SELECT simple_id FROM utilisateurs_mapping
            WHERE simple_id = ?
        ''', (discord_id,))

        result = cursor.fetchone()

        if result:
            simple_id = result[0]

            # Récupérer les statistiques de l'utilisateur avec le simple_id
            cursor.execute('''
                SELECT cc FROM utilisateurs
                WHERE discord_id = ?
            ''', (simple_id,))

            user_data = cursor.fetchone()

            if user_data:
                cc = user_data[0]
                resultat_de = random.randint(1, 100)
                
                # Stocker le résultat du D100CC dans recent_rolls
                recent_rolls[(discord_id, cible_id)] = resultat_de
                
                if resultat_de > cc:
                    reponse = f"❌ Tu as lancé un {resultat_de}, ce qui est supérieur à ta statistique CC de {cc}, c'est donc un échec ! ❌"
                else:
                    reponse = f"✅ Tu as lancé un {resultat_de}, ce qui est inférieur ou égal à ta statistique CC de {cc}, ce qui veut dire que tu réussis ton jet ! ✅"
            else:
                reponse = f"Aucune donnée trouvée pour l'utilisateur avec l'ID Discord {discord_id}."
        else:
            reponse = f"Aucune correspondance trouvée pour l'utilisateur avec l'ID Discord {discord_id}."
    finally:
        conn.close()
    
    await interaction.response.send_message(reponse)
      
@bot.tree.command(guild=discord.Object(id=0), name="switch", description="Change l'arme équipée de l'utilisateur")
async def switch(interaction: discord.Interaction):
    discord_id = interaction.user.id

    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Récupérer l'ID utilisateur à partir du discord_id
    cursor.execute('''
    SELECT simple_id
    FROM utilisateurs_mapping
    WHERE discord_id = ?
    ''', (discord_id,))
    user_id_result = cursor.fetchone()

    if user_id_result is None:
        await interaction.response.send_message("Aucun utilisateur trouvé.", ephemeral=True)
        conn.close()
        return

    user_id = user_id_result[0]

    # Récupérer la liste des armes possédées par l'utilisateur
    cursor.execute('''
    SELECT armes_nom
    FROM user_inventory
    WHERE utilisateur_id = ? AND equipped = 0
    ''', (user_id,))
    weapons = cursor.fetchall()

    # Si aucune arme n'est trouvée
    if not weapons:
        await interaction.response.send_message("Vous n'avez pas d'armes dans votre inventaire.", ephemeral=True)
        conn.close()
        return

    # Formatage des armes pour le menu déroulant
    weapon_list = [weapon[0] for weapon in weapons if weapon[0] and weapon[0].lower() != 'none']
    view = SwitchWeaponView(weapon_list, user_id)

    # Envoyer le message avec le menu déroulant, uniquement visible pour l'utilisateur qui a lancé la commande
    await interaction.response.send_message(
        "Choisissez une arme à équiper:", 
        view=view, 
        ephemeral=True
    )

    conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="inv", description="Affiche l'inventaire d'un utilisateur")
async def inv(interaction: discord.Interaction, discord_id: int):
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id à partir de l'ID Discord
        cursor.execute('''
            SELECT simple_id, Name FROM utilisateurs_mapping
            WHERE simple_id = ?
        ''', (discord_id,))
        
        result = cursor.fetchone()
        
        if result:
            simple_id, Name = result

            # Récupérer les objets de l'inventaire pour cet utilisateur
            cursor.execute('''
                SELECT armes_nom, armures_nom, divers_nom, argent 
                FROM user_inventory 
                WHERE utilisateur_id = ?
            ''', (simple_id,))
            
            inventory_data = cursor.fetchall()

            if inventory_data:
                weapons = []
                armors = []
                items = []
                money = 0

                # Organiser les données
                for row in inventory_data:
                    armes_nom, armures_nom, divers_nom, argent = row
                    
                    if armes_nom:
                        weapons.append(armes_nom)
                    if armures_nom:
                        armors.append(armures_nom)
                    if divers_nom:
                        items.append(divers_nom)
                    if argent:
                        money += argent

                # Créer un embed pour afficher l'inventaire
                embed = discord.Embed(title="Inventaire Utilisateur", description=f"Inventaire de {Name}", color=discord.Color.green())
                
                embed.add_field(name="Armes", value='\n'.join(weapons) if weapons else "Aucune arme", inline=False)
                embed.add_field(name="Armures", value='\n'.join(armors) if armors else "Aucune armure", inline=False)
                embed.add_field(name="Objets Divers", value='\n'.join(items) if items else "Aucun objet divers", inline=False)
                embed.add_field(name="Argent", value=f"{money} pièces" if money else "Aucun argent", inline=False)

                embed.set_footer(text=random.choice(liste_embed))
                embed.timestamp = datetime.datetime.now()
                
                await interaction.response.send_message(embed=embed, ephemeral=False)
            else:
                await interaction.response.send_message(f"Aucun inventaire trouvé pour l'utilisateur {Name}.", ephemeral=False)
        else:
            await interaction.response.send_message(f"Aucun utilisateur trouvé pour l'ID Discord {discord_id}.", ephemeral=False)
    
    finally:
        conn.close()
          
@bot.tree.command(guild=discord.Object(id=0), name="monid", description="Affiche le simple_id de l'utilisateur")
async def monid(interaction: discord.Interaction):
    discord_id = str(interaction.user.id)
    
    # Connexion à la base de données
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    try:
        # Récupérer le simple_id à partir de l'ID Discord
        cursor.execute('''
            SELECT simple_id FROM utilisateurs_mapping
            WHERE discord_id = ?
        ''', (discord_id,))
        
        result = cursor.fetchone()
        
        if result:
            simple_id = result[0]
            await interaction.response.send_message(f"Votre id est : {simple_id}", ephemeral=True)
        else:
            await interaction.response.send_message("Aucun simple_id trouvé pour votre ID Discord.", ephemeral=True)
    
    finally:
        conn.close()

@bot.tree.command(guild=discord.Object(id=0), name="help", description="Affiche la liste des commandes disponibles")
async def help_command(interaction: discord.Interaction):
    # Créer un embed pour afficher la liste des commandes
    embed = discord.Embed(title="Commandes du Bot", description="Voici la liste des commandes disponibles:", color=discord.Color.blue())
    
    # Ajouter des champs pour chaque commande avec une description
    embed.add_field(name="/monid", value="Affiche lid de l'utilisateur. Utile pour toutes les commandes ou presques !", inline=False)
    embed.add_field(name="/d100cc", value="Lance un dé à 100 faces et compare le résultat à la statistique CC de l'utilisateur.", inline=False)
    embed.add_field(name="/d100ct", value="Lance un dé à 100 faces et compare le résultat à la statistique CT de l'utilisateur.", inline=False)
    embed.add_field(name="/d6", value="Lance un dé à 6 faces.", inline=False)
    embed.add_field(name="/switch", value="Permet de changer d'arme équipée. Usage : /switch <ID Discord> <Nom de l'arme>", inline=False)
    embed.add_field(name="/stats", value="Affiche les statistiques d'un utilisateur. Usage : /stats <ID Discord>", inline=False)
    embed.add_field(name="/inv", value="Affiche l'inventaire d'un utilisateur. Usage : /inv <ID Discord>", inline=False)
    embed.add_field(name="/plandecarriere", value="Affiche le plan de carrière d'un utilisateur. Usage : /plandecarriere <ID Discord>", inline=False)
    embed.add_field(name="/comp", value="Affiche la liste des compétences d'un utilisateur. Usage : /comp <ID Discord>", inline=False)
    embed.add_field(name="/sorts", value="Affiche la liste des sorts d'un utilisateur. Usage : /sorts <ID Discord>", inline=False)
    embed.timestamp = datetime.datetime.now()
    
    await interaction.response.send_message(embed=embed, ephemeral=False)
              
@bot.event
async def on_ready():
    # Synchronisation des commandes
    await bot.tree.sync(guild=discord.Object(id=0))
    print(f"Connecté en tant que {bot.user}")
        
bot.run('')

