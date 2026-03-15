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
        String regex = "(?s)(!\\[([^\\]]*)\\]\\(([^)]+)\\))|(<img\\s+[^>]*?>)";
        Pattern pattern = Pattern.compile(regex);
        Matcher matcher = pattern.matcher(content);
        HashSet<String> picturesInMarkdown = new HashSet<>();

        while (matcher.find()) {
            String ref = matcher.group(0);
            String picture = null;
            
            if (ref.startsWith("!")) {
                int startParen = ref.indexOf('(');
                int endParen = ref.lastIndexOf(')');
                if (startParen != -1 && endParen != -1 && endParen > startParen) {
                    picture = ref.substring(startParen + 1, endParen).trim();
                    if (picture.contains(" ")) {
                        int spaceIndex = picture.indexOf(' ');
                        if (spaceIndex > 0) {
                            String potentialPath = picture.substring(0, spaceIndex);
                            if (potentialPath.endsWith("\"") || potentialPath.endsWith("'")) {
                                picture = potentialPath;
                            }
                        }
                    }
                }
            } else if(ref.startsWith("<img")){
                String regex2 = "src=\"([^\"]+)";
                Pattern pattern2 = Pattern.compile(regex2);
                Matcher matcher2 = pattern2.matcher(ref);
                if(matcher2.find()){
                    picture = matcher2.group(1);
                }
            }

            if (picture != null && !picture.isEmpty()) {
                picture = picture.replace("\\", "/");
                int lastSlash = picture.lastIndexOf("/");
                if (lastSlash >= 0 && lastSlash < picture.length() - 1) {
                    picture = picture.substring(lastSlash + 1);
                }
                picturesInMarkdown.add(picture);
            }

        }
            System.out.println("MarkDown 中一共有：" + picturesInMarkdown.size() + "个图片文件");
            String[] extensions = { "png", "jpg", "jpeg", "bmp", "webp", "gif", "svg", "tiff"};
            boolean recursive = false;
            HashSet<String> picturesInDirectory = new HashSet<String>();
            Collection<File> files = FileUtils.listFiles(picDirFile, extensions, recursive);
            System.out.println("图片目录下一共有：" + files.size() + "个图片文件");

            for (File pic : files) {
                picturesInDirectory.add(pic.getName().toLowerCase());
            }

            HashSet<String> picturesInMarkdownLower = new HashSet<>();
            for (String pic : picturesInMarkdown) {
                picturesInMarkdownLower.add(pic.toLowerCase());
            }

            picturesInDirectory.removeAll(picturesInMarkdownLower);
            int count = 0;
            for (String pictLower : picturesInDirectory) {
                for (File picFile : files) {
                    if (picFile.getName().toLowerCase().equals(pictLower)) {
                        String pic = picDir + File.separator + picFile.getName();
                        System.out.println("删除图片：" + pic);
                        FileUtils.deleteQuietly(picFile);
                        count++;
                        break;
                    }
                }
            }
            System.out.println("操作完成，共删除了" + count + "个图片文件！");
            return true;
    }

    public static void main(String[] args) {
         System.out.println("=== MarkDown 下冗余图片清理工具 (kevin，单文件版) ===");

         Scanner scanner = new Scanner(System.in);

         try {
             System.out.println("请输入 Markdown 文件的路径和文件名 (可直接将 md 文件拖到命令窗口)：");
             String path = scanner.nextLine();

             System.out.println("请输入图片目录 (默认为文件同目录下：[文件名].assets)：");
             String picDir = scanner.nextLine();

             delAssets(path, picDir);
         } catch (Exception e) {
             System.out.println("发生错误：" + e.getMessage());
             e.printStackTrace();
         } finally {
             scanner.close();
         }
    }

}