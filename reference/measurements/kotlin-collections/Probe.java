import kotlin.collections.CollectionsKt;
import java.util.*;

public class Probe {
    static void probe(String label, List<String> l) {
        System.out.println(label + " -> runtime class: " + l.getClass().getName());
        try { l.add("X"); System.out.println("   add() SUCCEEDED, now = " + l); }
        catch (Throwable t) { System.out.println("   add() threw: " + t.getClass().getName()); }
        try { l.set(0, "Y"); System.out.println("   set() SUCCEEDED, now = " + l); }
        catch (Throwable t) { System.out.println("   set() threw: " + t.getClass().getName()); }
        System.out.println("   instanceof java.util.List = " + (l instanceof java.util.List));
    }
    public static void main(String[] a) {
        System.out.println("kotlin-stdlib: " + CollectionsKt.class.getProtectionDomain().getCodeSource().getLocation());
        probe("listOf()        [0 elems]", CollectionsKt.<String>emptyList());
        probe("listOf(\"a\")     [1 elem ]", CollectionsKt.listOf("a"));
        probe("listOf(\"a\",\"b\") [2 elems]", CollectionsKt.listOf(new String[]{"a","b"}));
        // read-only VIEW over a mutable list: does Java see it as mutable?
        List<String> backing = CollectionsKt.mutableListOf(new String[]{"a","b"});
        System.out.println("mutableListOf -> " + backing.getClass().getName());
        probe("view of mutableListOf (typed List in Kotlin)", backing);
        System.out.println("Java List.of()               -> " + List.of("a","b").getClass().getName());
        System.out.println("Collections.unmodifiableList -> " + Collections.unmodifiableList(new ArrayList<>(List.of("a"))).getClass().getName());
    }
}
