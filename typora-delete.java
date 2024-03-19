package org.newboy.utils;

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
 */
public class MarkDownPictureCleaner {

    public static void main(String[] args) {
        System.out.println("=== MarkDown下冗余图片清理工具(开发者：NewBoy 版本：1.0) ===");

        Scanner scanner = new Scanner(System.in);

        // MarkDown的文件名
        String path = null;
        try {
            System.out.println("请输入Markdown文件的路径和文件名(可直接将md文件拖到命令窗口)：");
            path = scanner.nextLine();
        } catch (Exception e) { // 用户可能按下 Ctrl + C 终止程序
            System.out.println("程序结束！");
            scanner.close();
            System.exit(0);
        }

        // 预检查，判断用户输入的文件是否存在
        File file = null;

        // 图片所在目录
        String picDir = null;

        // if (StringUtils.isNotBlank(path)) {
        if ("".equals(path.trim())) {
            // 如果用户在DOS命令窗口拖入，前后有双引号，去掉双引号
            path = path.trim().replace("\"", "");
            // 创建文件对象
            file = new File(path);
            if (!file.exists()) {
                System.out.println("Markdown文件不存在！");
                file = null;
            } else {
                System.out.println("请输入图片目录(默认为文件同目录下：[文件名].assets)：");
                // 图片所在目录
                picDir = scanner.nextLine();
                // 如果为空，空串，或者空格
                // if (StringUtils.isBlank(picDir)) {
                if ("".equals(picDir.trim())) {
                    // picDir = "assets";
                    // String rootPath = file.getParent();
                    picDir = file.getName() + ".assets";
                }
                System.out.println("图片目录为：" + picDir);
            }
        }

        // 读取 Markdown 文件的内容
        String content = null;
        if (file != null) { // 如果用户输入的文件不存在，跳过此次操作
            System.out.println("您输入的路径：" + file.getAbsolutePath());
            try {
                content = FileUtils.readFileToString(file, "UTF-8");
            } catch (IOException e) {
                System.out.println("文件读取异常：" + e.getMessage());
                content = null;
            }
        }

        if (content != null) {
            // 找出 Markdown 文件中所有图片的引用
            String regex = "(![.*])((.*))|(<img \b.*?(?:>|/>))"; // 捕获组，匹配类似于 "![*](*)" 的字符串
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
                }
                // else if (ref.startsWith("<")) { // 或者以<开头的
                // beginIndex = ref.indexOf("/") + 1;
                // endIndex = ref.indexOf('"', beginIndex);
                // }
                picture = ref.substring(beginIndex, endIndex);
                // logger.info(picture);
                // 保存图片名称
                picturesInMarkdown.add(picture);
            }

            System.out.println("MarkDown中一共有：" + picturesInMarkdown.size() + "个图片文件");
            // 列出 Markdown 文件所在目录中的图片名称
            File directory = file.getParentFile();
            String[] extensions = { "png", "jpg", "jpeg", "bmp" }; // 图片扩展名
            boolean recursive = true; // 不扫描子目录
            HashSet<String> picturesInDirectory = new HashSet<String>();
            // 获取所有文件的集合
            Collection<File> files = FileUtils.listFiles(directory, extensions, recursive);
            System.out.println("图片目录下一共有：" + files.size() + "个图片文件");

            for (File picture : files) {
                String name = picture.getName();
                picturesInDirectory.add(name);
            }

            // 列出冗余图片，并将其删除
            picturesInDirectory.removeAll(picturesInMarkdown);
            int count = 0;
            for (String picture : picturesInDirectory) {
                String pic = directory.getAbsolutePath() + File.separator + picDir + File.separator + picture;

                System.out.println("删除图片：" + pic);
                FileUtils.deleteQuietly(new File(pic));
                count++;
            }
            System.out.println("操作完成，共删除了" + count + "个图片文件！");
        }

        scanner.close();
        System.exit(0);
    }
}