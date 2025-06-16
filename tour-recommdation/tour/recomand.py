
from math import sqrt, pow
import operator


class UserCf():
    # 获得初始化数据
    def __init__(self, data):
        self.data = data


    #def getItems(self, username1, username2):
       # return self.data[username1], self.data[username2]

    # 计算两个用户的皮尔逊相关系数
    def pearson(self, user1, user2):
        sumAB = 0.0
        n = 0
        sumA = 0.0
        sumB = 0.0
        sumA2 = 0.0
        sumB2 = 0.0
        try:
            for view1, grade1 in user1.items():
                if view1 in user2.keys():  # 计算公共的旅游产品的评分
                    n += 1
                    sumAB += grade1 * user2[view1]
                    sumA += grade1
                    sumB += user2[view1]
                    sumA2 += pow(grade1, 2)
                    sumB2 += pow(user2[view1], 2)

            fenzi = sumAB - (sumA * sumB) / n
            fenmu = sqrt((sumA2 - pow(sumA, 2) / n) * (sumB2 - pow(sumB, 2) / n))
            p = fenzi / fenmu
        except Exception:
            print("异常信息")
            return None
        return p

    # 计算与当前用户的距离，获得最临近的用户
    def nearstUser(self, username, n=1):
        distances = {}  # 用户，相似度
        for otherUser, items in self.data.items():  # 遍历整个数据集
            if otherUser not in username:  # 非当前的用户
                distance = self.pearson(self.data[username], self.data[otherUser])  # 计算两个用户的相似度
                if distance is None:
                     distance = 0
                distances[otherUser] = distance
        sortedDistance = sorted(distances.items(), key=operator.itemgetter(1), reverse=True)  # 最相似的N个用户
        print("排序后的用户为：" + str(sortedDistance))
        return sortedDistance[:n]

    # 给用户推荐旅游产品
    def recomand(self, username, n=1, min_score=4):
        recommand = {}
        for similar_user, _ in dict(self.nearstUser(username, n)).items():
            for product, score in self.data[similar_user].items():
                if product not in self.data[username].keys() and score >= min_score:
                    if product not in recommand:
                        recommand[product] = score
        return sorted(recommand.items(), key=operator.itemgetter(1), reverse=True)


if __name__ == '__main__':
    users = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                           'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                           'The Night Listener': 3.0},

             'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                              'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                              'You, Me and Dupree': 3.5},

             'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                  'Superman Returns': 3.5, 'The Night Listener': 4.0},

             'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                              'The Night Listener': 4.5, 'Superman Returns': 4.0,
                              'You, Me and Dupree': 2.5},

             'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                              'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                              'You, Me and Dupree': 2.0},

             'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                               'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},

             'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}
             }

    userCf = UserCf(data=users)
    recommandList = userCf.recomand('Toby', 2)
    print("最终推荐：")
    for r in recommandList:
        print(r)

