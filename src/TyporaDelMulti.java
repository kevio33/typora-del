package src;

// import org.apache.commons.lang3.StringUtils;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.util.Scanner;

/**
 * 通过输入的目录自动检索该目录下的所有子目录，逐个便利子目录的md文件
 * 注意：该删除只针对'.assets'文件和'.md'在同一目录下情况
 */
public class TyporaDelMulti {

    private static int count = 0;//记录处理的文件数量
    private static StringBuffer stringBuffer;
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
//            scanner.close();
            System.exit(0);
        }finally {
            scanner.close();
        }

        // 判断该路径是否合法
        try {
            if (isValidDir(rootPath)) {
                // 如果是个文件，那么直接调用单文件的库即可
                File file = new File(rootPath);
                System.out.println("-------------------------------------------------------------");
                System.out.println("正在处理中：");
                stringBuffer = new StringBuffer();
                deletePic(file);
                System.out.println("处理完毕：一共处理文件"+count+"个。详情请看log日志");
                System.out.println("-------------------------------------------------------------");

                File fileLog = new File(file.getAbsolutePath()+"/"+"delete_log.log");//打印日志
                BufferedOutputStream bufferedOutputStream = new BufferedOutputStream(new FileOutputStream(fileLog));
                byte[] bytes = stringBuffer.toString().getBytes();
                bufferedOutputStream.write(bytes);
                bufferedOutputStream.flush();
                bufferedOutputStream.close();
            }else{
                System.out.println("输入路径不是一个目录");
            }
        } catch (Exception e) {
            // TODO Auto-generated catch block
            System.out.println(e.getMessage());
        }
    }

    //删除多余的图片
    private static void deletePic(File file) throws Exception {

        if(file.getName().contains(".assets")){
            return;
        }

        for(File subFile :file.listFiles()){

            if (subFile==null){
                continue;
            }
            if(subFile.isDirectory()){
                deletePic(subFile);
            }else if(subFile.getName().contains(".md")){
                if(Typoradel.delAssets(subFile.getAbsolutePath(),null)){
                    count++;
                    stringBuffer.append(subFile.getName()).append("\n");
                    System.out.println("###################");
                }
            }
        }
    }

    // 判断路径是否合法且是否为目录
    private static boolean isValidDir(String rootPath) throws Exception {
        File file = new File(rootPath);

        if (!file.exists()) {
            throw new Exception("无法找到该目录");// 该路径不存在
        }

        if (file.isDirectory()) {
            // 如果是一个目录
            return true;
        }
        return false;
    }
}
