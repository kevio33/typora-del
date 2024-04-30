package src;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.HashSet;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * @author NewBoy
 * @version 1.0
 * @since 2020-12-04
 *        删除MarkDown目录下多余的图片文件
 *        只能指定单个文件和单个目录
 */
public class Typoradel {

    static boolean delAssets(String path, String picDir2) throws Exception {

        // 预检查，判断用户输入的文件是否存在
        File file = null;

        // 图片所在目录
        String picDir = picDir2;
        File picDirFile = null;
        // 检查输入路径是否为空
        if (StringUtils.isNotBlank(path)) {
            // 如果用户在DOS命令窗口拖入，前后有双引号，去掉双引号
            path = path.trim().replace("\"", "");
            file = new File(path);
            // 文件不存在
            if (!file.exists()) {
                // System.out.println("Markdown文件不存在！");
                file = null;
                throw new Exception("Markdown文件不存在！");
            } else {
                // 判断pic是否为空
                if (StringUtils.isBlank(picDir)) {
                    picDir = StringUtils.substringBefore(file.getAbsolutePath(),".")+".assets";
                }

                picDirFile = new File(picDir);
                if(!picDirFile.isDirectory()){
                    return false;
                }
                System.out.println("图片目录为：" + picDir);
            }
        } else {
            // 输入路径为空
            throw new Exception("输入路径不能为空");
        }

        // 读取 Markdown 文件的内容
        String content = null;
        // if (file != null) { // 如果用户输入的文件不存在，跳过此次操作
        System.out.println("文件路径：" + file.getAbsolutePath());
        try {
            content = FileUtils.readFileToString(file, "UTF-8");
        } catch (IOException e) {
            System.out.println("文件读取异常：" + e.getMessage());
            content = null;
        }
        // }

        // if (content != null) {
        // 找出 Markdown 文件中所有图片的引用
        // String regex = "(![.*])((.*))|(<img \b.*?(?:>|/>))"; // 捕获组，匹配类似于 "![*](*)"
        // 的字符串
        String regex = "(!\\[.*\\]\\(.*\\))|(<img \\b.*?(?:>|/>))";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(content);
        HashSet<String> picturesInMarkdown = new HashSet<>();

        while (matcher.find()) {
            String ref = matcher.group(0);
            String picture = null;
            int beginIndex = 0;
            int endIndex = 0;
            // 如果是!开头
            if (ref.startsWith("!")) {
                // 获取图片名称
                beginIndex = ref.lastIndexOf("/") + 1;
                endIndex = ref.length() - 1;
            }else if(ref.startsWith("<img")){
//                String regex2 = "src=\".*\"";
                String regex2 = "src=\"([^\"]+)";
                Pattern pattern2 = Pattern.compile(regex2);
                Matcher matcher2 = pattern2.matcher(ref);
                if(matcher2.find()){
                    ref = matcher2.group();
                    beginIndex = ref.indexOf("/") + 1;
                    endIndex = ref.length();
                }
            }

            picture = ref.substring(beginIndex, endIndex);
            // 保存图片名称
            picturesInMarkdown.add(picture);

        }
            System.out.println("MarkDown中一共有：" + picturesInMarkdown.size() + "个图片文件");
            // 列出 Markdown 文件所在目录中的图片名称
//            File directory = file.getParentFile();
            String[] extensions = { "png", "jpg", "jpeg", "bmp" ,"webp"}; // 图片扩展名
            boolean recursive = false; // 不扫描子目录
            HashSet<String> picturesInDirectory = new HashSet<String>();
            // 获取所有文件的集合
            Collection<File> files = FileUtils.listFiles(picDirFile, extensions,recursive);//列出目录下所有符合条件的文件
            System.out.println("图片目录下一共有：" + files.size() + "个图片文件");

            for (File pic : files) {
                String name = pic.getName();
                picturesInDirectory.add(name);
            }

            // 列出冗余图片，并将其删除
            picturesInDirectory.removeAll(picturesInMarkdown);
            int count = 0;
            for (String pict : picturesInDirectory) {
                String pic =  picDir + File.separator + pict;

                System.out.println("删除图片：" + pic);
                FileUtils.deleteQuietly(new File(pic));
                count++;
            }
            System.out.println("操作完成，共删除了" + count + "个图片文件！");
            return true;
    }

    public static void main(String[] args) {
         System.out.println("=== MarkDown下冗余图片清理工具(kevin,单文件版) ===");

         Scanner scanner = new Scanner(System.in);

         // MarkDown的文件名
         String path = null;
         String picDir = null;
         try {
             System.out.println("请输入Markdown文件的路径和文件名(可直接将md文件拖到命令窗口)：");
             path = scanner.nextLine();

             System.out.println("请输入图片目录(默认为文件同目录下：[文件名].assets)：");
             // 图片所在目录
             picDir = scanner.nextLine();

         } catch (Exception e) { // 用户可能按下 Ctrl + C 终止程序
             System.out.println("程序结束！");
             scanner.close();
             System.exit(0);
         }

         scanner.close();
         try {
             delAssets(path, picDir);
         } catch (Exception e) {
             // TODO Auto-generated catch block
             System.out.println(e.getMessage());
         }
    }

}