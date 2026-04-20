import random

print("--- โปรแกรมทายใจโดย Gemini ---")
secret_number = random.randint(1, 10)

print("ฉันแอบคิดเลข 1 ถึง 10 ไว้ในใจ...")
guess = int(input("ลองทายซิว่าเลขอะไร: "))

if guess == secret_number:
    print(f"ยินดีด้วย! คุณทายถูก เลขนั้นคือ {secret_number} จริงๆ")
else:
    print(f"เสียใจด้วยนะ เลขที่ฉันคิดคือ {secret_number} ต่างหาก")

print("--- จบการทดสอบ ---")