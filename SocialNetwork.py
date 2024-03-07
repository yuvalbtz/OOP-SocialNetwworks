from abc import ABC, abstractmethod
from enum import Enum


class PostType(Enum):
    TEXT = "Text"
    IMAGE = "Image"
    SALE = "Sale"


class PostsFactory:
    @staticmethod
    def create_post(p_type: str, owner, *args):
        if p_type == PostType.TEXT.value:
            return TextPost(owner, *args)
        elif p_type == PostType.IMAGE.value:
            return ImagePost(owner, *args)
        elif p_type == PostType.SALE.value:
            return SalePost(owner, *args)


class Post:
    likes = set()
    comments = []
    owner = ''

    def __init__(self, owner):
        self.owner = owner

    def like(self, user):
        net = SocialNetwork("")
        if net.is_online(user.name):
            self.likes.add(user.name)
            if self.owner != user:
                notification_message = f"{user.name} liked your post"
                self.owner.update("Like", user, notification_message)

    def comment(self, user, desc):
        net = SocialNetwork("")
        if net.is_online(user.name):
            self.comments.append((user, desc))
            if self.owner.name != user.name:
                self.owner.update("Comment", user, desc)

    def __post_as_string(self):
        pass

    def print_post(self):
        pass


class TextPost(Post):
    content = ""

    def __init__(self, owner, content):
        super().__init__(owner)
        self.content = content
        self.print_post()
        msg = self.__post_as_string()
        owner.notify("Post", msg)

    def print_post(self):
        print(self.__post_as_string())

    def __post_as_string(self):
        return f"{self.owner.name} published a post:\n\"{self.content}\"\n"

    def __str__(self):
        return self.__post_as_string()


class ImagePost(Post):
    image_url = ""

    def __init__(self, owner, image_url):
        super().__init__(owner)
        self.image_url = image_url
        self.print_post()
        msg = self.__post_as_string()
        owner.notify("Post", msg)

    def display(self):
        try:
            print("Shows picture")
        except FileNotFoundError:
            print("No image found")
        return

    def print_post(self):
        print(self.__post_as_string())

    def __post_as_string(self):
        return f"{self.owner.name} posted a picture\n"

    def __str__(self):
        return self.__post_as_string()


class SalePost(Post):
    text = ""
    price = 0.0
    location = ""
    is_sold = False
    amountOfDiscount = 0.0

    def __init__(self, owner, *args):
        super().__init__(owner)
        text, price, location = args
        self.text = text
        self.price = float(price)
        self.location = location
        self.is_sold = False
        self.print_post()
        self.owner.notify("Post", self.__post_as_string())

    def discount(self, amount_of_discount, password):
        if self.owner.correct_password(password):
            self.price = self.price * (1 - amount_of_discount / 100)
            msg = f"Discount on {self.owner.name} product! the new price is: {self.price}"
            print(msg)
        return self

    def sold(self, password):
        if self.owner.correct_password(password):
            self.is_sold = True
            print(f"{self.owner.name}'s product is sold")

    def print_post(self):
        print(self.__post_as_string())

    def __str__(self):
        return self.__post_as_string()

    def __post_as_string(self):
        sold_text = "Sold!" if self.is_sold else "For sale!"
        price_update = self.price if self.is_sold else int(self.price)
        msg = f"{self.owner.name} posted a product for sale:\n"
        msg = msg + f"{sold_text} {self.text}, price: {price_update}, pickup from: {self.location}\n"
        return msg


class User:
    def __init__(self, name):
        self.followers = []
        self.notifications = []
        self.name = name
        self.posts_num = 0

    def notify(self, action: str, message: str):
        for follower in self.followers:
            follower.update(action, self, message)

    def update(self, action: str, sender, msg: str):
        notification = ""
        if action == "Post":
            notification = f"{sender.name} has a new post"
        elif action == "Like":
            notification = f"{sender.name} liked your post"
            print(f"notification to {self.name}: {notification}")
        elif action == "Comment":
            notification = f"{sender.name} commented on your post"
            print(f"notification to {self.name}: {notification}: {msg}")
        self.notifications.append(notification)

    def add_follower(self, follower):
        if follower not in self.followers:
            self.followers.append(follower)

    def remove_follower(self, follower):
        if follower in self.followers:
            self.followers.remove(follower)

    def follow(self, followee):
        followee.add_follower(self)
        s = self.name + " started following " + followee.name
        print(s)
        return

    def unfollow(self, followee):
        followee.remove_follower(self)
        s = self.name + " unfollowed " + followee.name
        print(s)
        return

    def publish_post(self, post_type, *args):
        p = PostsFactory.create_post(post_type, self, *args)
        self.posts_num += 1
        return p

    def print_notifications(self):
        print(f"{self.name}'s notifications:")
        for notification in self.notifications:
            print(notification)

    def correct_password(self, password):
        net = SocialNetwork("")
        psw = net.allUsers.get(self.name, ("", password))[1]
        return psw == password

    def __str__(self):
        return (f"User name: {self.name}, Number of posts: {self.posts_num}, "
                f"Number of followers: {len(self.followers)}")


class Member(ABC):
    @abstractmethod
    def update(self, newsletter):
        pass


class SocialNetwork(object):
    name = ""
    _instance = None  # Singleton ->  Single instance of the SocialNetwork class
    allUsers = dict()  # Im using a dictionary for storing all of the users that are registered

    def __new__(cls, name):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.name = name
            cls._instance.logged_in = list()
            print(f"The social network {cls._instance.name} was created!")
        return cls._instance

    def sign_up(self, name, password):
        if self.good_password(password) and not self.is_name_exists(name):
            usr = User(name)
            self.allUsers[name] = (usr, password)
            self.logged_in.append(name)
            return usr
        return None

    def is_name_exists(self, name):
        return name in self.allUsers

    def good_password(self, password):
        return 4 <= len(password) <= 8

    def is_online(self, user_name):
        return user_name in self.logged_in

    def log_in(self, name, password):
        user_and_password = self.allUsers.get(name)
        if user_and_password and user_and_password[1] == password and name not in self.logged_in:
            self.logged_in.append(name)
            print(f"{name} connected")

    def log_out(self, name):
        if name in self.logged_in:
            self.logged_in.remove(name)
            print(f"{name} disconnected")

    def __str__(self):
        prt = f"{self.name} social network:"
        for name, unp in self.allUsers.items():
            prt += "\n" + str(unp[0])
        prt += "\n"
        return prt
