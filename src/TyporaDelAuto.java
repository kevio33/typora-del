package src;

import org.apache.commons.io.FileUtils;
// import org.apache.commons.lang3.StringUtils;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.HashSet;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 通过输入的目录自动检索该目录下的所有子目录，逐个便利子目录的md文件
 * 注意：该删除只针对'.assets'文件和'.md'在同一目录下情况
 */
public class TyporaDelAuto {
    public static void main(String[] args) {
        System.out.println("=== MarkDown下冗余图片清理工具(kevin,多文件版) ===");

        Scanner scanner = new Scanner(System.in);

        // 根目录名，该目录下面包含md文件
        String rootPath = null;
        try {
            System.out.println("请输入根目录路径(可直接拖拽)：");
            rootPath = scanner.nextLine();
        } catch (Exception e) { // 用户可能按下 Ctrl + C 终止程序
            System.out.println("程序结束！");
            scanner.close();
            System.exit(0);
        }

        // 判断该路径是否合法
        try {
            if (!isValidDir(rootPath)) {
                // 如果是个文件，那么直接调用单文件的库即可
            }
        } catch (Exception e) {
            // TODO Auto-generated catch block
            System.out.println("无法找到输入目录");
        }
    }

    // 判断路径是否合法
    private static boolean isValidDir(String rootPath) throws Exception {
        File file = new File(rootPath);

        if (!file.exists()) {
            throw new Exception();// 该路径不存在
        }

        if (file.isDirectory()) {
            // 如果是一个目录
            return true;
        }

        return false;

    }
}
