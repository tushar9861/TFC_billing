import codecs

lines = codecs.open('distributor_dashboard.py', 'r', 'utf-8').readlines()
main_start = -1
for i, l in enumerate(lines):
    if 'if __name__ == "__main__":' in l:
        main_start = i - 1  # include the comment
        break

if main_start != -1:
    main_end = -1
    for i in range(main_start + 2, len(lines)):
        if 'def _build_sql_tab' in lines[i] or lines[i].startswith('class '):
            main_end = i
            break
            
    if main_end != -1:
        main_block = lines[main_start:main_end]
        del lines[main_start:main_end]
        lines.extend(main_block)
        codecs.open('distributor_dashboard.py', 'w', 'utf-8').writelines(lines)
