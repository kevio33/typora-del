package src;

import java.io.File;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.*;

public class Test {
    public static void main(String[] args) {
        try {
            String content = FileUtils.readFileToString(new File("C:\\Users\\Administrator\\Desktop\\test\\hello.md"), "UTF-8");
            String regex = "!\\[.*\\]\\(.*\\)";
            Pattern pattern = Pattern.compile(regex);
            Matcher matcher = pattern.matcher(content);


            while (matcher.find()) {
                System.out.println(matcher.group(0));
//                System.out.printf(matcher.group(1));
            }
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
}
