import java.util.Scanner;

public class TestGemini {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("--- โปรแกรมทดสอบระบบโดย Gemini ---");
        System.out.print("กรุณาใส่ตัวเลขตัวที่ 1: ");
        int num1 = input.nextInt();

        System.out.print ("กรุณาใส่ตัวเลขตัวที่ 2: ");
        int num2 = input.nextInt();

        int result = num1 + num2;
        System.out.println("ผลรวมของตัวเลขทั้งสองคือ: " + result);
        System.out.println("--- ทำงานสำเร็จ! ---");
        
        input.close();
    }
}